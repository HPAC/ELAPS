#include "Sampler.hpp"

#include <cstdlib>
#include <cstring>
#include <iostream>
#include <sstream>
#include <iterator>

#ifdef PAPI
#include <papi.h>
#endif

#include CFG_H
#include "sample.h"

using namespace std;

void Sampler::set_counters(const vector<string> &tokens) {
#ifdef PAPI
    // ignore excess counters
    const int maxcounters = PAPI_num_counters();
    size_t ncounters = tokens.size() - 1;
    if (ncounters > maxcounters) {
        cerr << "Too many counters specified: given " << ncounters;
        cerr << " maximum " << maxcounters << " (truncating counter list)" << endl;
        ncounters = maxcounters;
    }

    // clear old counters
    counters.clear();

    // register new counters individually
    for (size_t i = 0; i < ncounters; i++) {

        // convert string to code
        int code;
        char str[PAPI_MAX_STR_LEN];  // need to pass a non-const *
        strcpy(str, tokens[i + 1].c_str());
        const int check = PAPI_event_name_to_code(str, &code);

        // check for errors
        if (check == PAPI_OK)
            counters.push_back(code);
        else if (check == PAPI_ENOTPRESET)
            cerr << "Counter unknown: " << tokens[i + 1] << " (counter ignored)" << endl;
        else if (check == PAPI_ENOEVNT)
            cerr << "Counter unavailable: " << tokens[i + 1] << " (counter ignored)" << endl;
    }
#else
    cerr << "PAPI support not enabled (command ignored)" << endl;
#endif
}

template <typename T>
void Sampler::named_malloc(const vector<string> &tokens, size_t multiplicity=1) {
    // require 2 arguments: name, size
    if (tokens.size() < 3) {
        cerr << "Too few arguments for " << tokens[0] << " (command ignored)" << endl; 
        cerr << "usage (example): " << tokens[0] << " A 10000" << endl;
        return;
    }
    if (tokens.size() > 3) {
        cerr << "Ignoring excess arguments for " << tokens[0] << endl; 
        cerr << "usage (example): " << tokens[0] << " A 10000" << endl;
    }

    // parse arguments
    const string &name = tokens[1];
    const size_t size = atoi(tokens[2].c_str()) * multiplicity;

    // check non-existance of name
    if (!mem.named_exists(name)) {
        cerr << "Variable already exists: " << name << " (command ignored)" << endl;
        return;
    }
    // name must beginn with letter
    if (!isalpha(name[0])) {
        cerr << "Variable name must begin with a letter: " << name << " (command ignored)" << endl;
        return;
    }

    //TODO: check size conversion error
    // size must be > 0
    if (size <= 0) {
        cerr << "Cannot allocate variable of non-positive size " << size << " (command ignored)" << endl;
        return;
    }

    // malloc the variabel
    mem.named_malloc<T>(name, size);
}

template <typename T>
void Sampler::named_offset(const vector<string> &tokens, size_t multiplicity=1) {
    // require 3 arguments: oldname, offset, newname
    if (tokens.size() < 4) {
        cerr << "Too few arguments for " << tokens[0] << " (command ignored)" << endl; 
        cerr << "usage (example): " << tokens[0] << " Old 10000 New" << endl;
        return;
    }
    if (tokens.size() > 4) {
        cerr << "Ignoring excess arguments for " << tokens[0] << endl; 
        cerr << "usage (example): " << tokens[0] << " Old 10000 New" << endl;
    }
    
    // parse arguments
    const string &oldname = tokens[1];
    const ssize_t offset = atoi(tokens[2].c_str()) * multiplicity;
    const string &newname = tokens[3];

    // check existence of oldname
    if (!mem.named_exists(oldname)) {
        cerr << "Unknown variable: " << oldname << " (command ignored)" << endl;
        return;
    }
    // TODO: check offset conversion errors
    // check non-existance of newname
    if (!mem.named_exists(oldname)) {
        cerr << "Variable already exists: " << newname << " (command ignored)" << endl;
        return;
    }

    // alias a new offset
    mem.named_offset<T>(oldname, offset, newname);
}

void Sampler::named_free(const vector<string> &tokens) {
    // require 1 argument: name
    if (tokens.size() < 2) {
        cerr << "Too few arguments for " << tokens[0] << " (command ignored)" << endl; 
        cerr << "usage (example): " << tokens[0] << " A" << endl;
        return;
    }
    if (tokens.size() > 2) {
        cerr << "Ignoring excess arguments for " << tokens[0] << endl; 
        cerr << "usage (example): " << tokens[0] << " A" << endl;
    }

    // parse arguments
    const string &name = tokens[1];

    // check existence
    if (!mem.named_exists(name)) {
        cerr << "Unknown variable: " << name << " (command ignored)" << endl;
        return;
    }

    // free the variabel
    mem.named_free(name);
}

void Sampler::add_call(const vector<string> &tokens) {
    const string &routine = tokens[0];

    // catch unknown routines
    if (signatures.find(routine) == signatures.end()) {
        cerr << "Uknown kernel: " << routine << " (call ignored)" << endl;
        return;
    }

    // (try to) set up a call parser for the kernel
    const Signature &signature = signatures[routine];
    try {
        CallParser callparser(tokens, signature, mem);
        callparsers.push_back(callparser);
    } catch (CallParserException &e) {
        // the call could not be parserd
        // (failure already reported)
    }
}

void Sampler::go() {
    size_t ncalls = callparsers.size();
    KernelCall *calls = new KernelCall[ncalls];

    // construct KernelCalls (C structs)
    for (size_t i = 0; i < ncalls; i++)
        calls[i] = callparsers[i].get_call();

    // run measurements
#ifdef PAPI
    sample(calls, ncalls, &counters[0], counters.size());
#else
    sample(calls, ncalls);
#endif

    // print results
    for (size_t i = 0; i < ncalls; i++) {
        cout << calls[i].rdtsc;
#ifdef PAPI
        for (size_t j = 0; j < counters.size(); j++)
            cout << "\t" << calls[i].counters[j];
#endif
        cout << endl;
    }

    // clean up
    delete [] calls;
    callparsers.clear();
    mem.static_reset();
}

void Sampler::add_signature(const Signature &signature) {
    signatures[signature.name] = signature;
}

void Sampler::start() {
    // read stdin by lines
    string line;
    while (getline(cin, line)) {

        // clear comments
        line = line.substr(0, line.find_first_of("#"));

        // remove leading spaces
        line = line.substr(line.find_first_not_of(" \t\n\v\f\r"));

        // ignore empty lines
        if (line.size() == 0)
            continue;

        // tokenize line
        vector<string> tokens;
        istringstream iss(line);
        copy(istream_iterator<string>(iss), istream_iterator<string>(), back_inserter(tokens));

        // check for special commands
        const string &command = tokens[0];

        // run sampler
        if (command == "go")
            go();

        // malloc
        else if (command == "malloc")
            named_malloc<char>(tokens);
        else if (command == "imalloc")
            named_malloc<int>(tokens);
        else if (command == "fmalloc")
            named_malloc<float>(tokens);
        else if (command == "dmalloc")
            named_malloc<double>(tokens);
        else if (command == "cmalloc")
            named_malloc<float>(tokens, 2);
        else if (command == "zmalloc")
            named_malloc<double>(tokens, 2); 

        // offset
        else if (command == "offset")
            named_offset<char>(tokens);
        else if (command == "ioffset")
            named_offset<int>(tokens);
        else if (command == "foffset")
            named_offset<float>(tokens);
        else if (command == "doffset")
            named_offset<double>(tokens);
        else if (command == "coffset")
            named_offset<float>(tokens, 2);
        else if (command == "zoffset")
            named_offset<double>(tokens, 2);

        // free
        else if (command == "free")
            named_free(tokens);

        // PAPI counters
        else if (command == "set_counters")
            set_counters(tokens);

        // check for kernel call
        else
            add_call(tokens);
    }

    // process remaining calls
    go();
}

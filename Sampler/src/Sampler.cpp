#include "Sampler.hpp"

#include <cstdlib>
#include <iostream>
#include <sstream>
#include <iterator>

#include CFG_H
#include "sample.h"

using namespace std;

void Sampler::set_counters(const vector<string> &tokens) {
#ifdef PAPI
    const int maxcounters = PAPI_num_counters();
    size_t ncounters = tokens.size() - 1;
    if (ncounters > maxcounters) {
        cerr << "Too many counters specified: given " << ncounters;
        cerr << " maximum " << maxcounters << " (truncating counter list)" << endl;
        ncounters = maxcounters;
    }
    counters.resize(0);
    for (size_t i = 0; i < ncounters; i++) {
        int code;
        const int check = PAPI_event_name_to_code(tokens[i + 1].c_str(), &code)
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
    if (tokens.size() < 3) {
        cerr << "Too few arguments for " << tokens[0] << " (command ignored)" << endl; 
        cerr << "usage (example): " << tokens[0] << " A 10000" << endl;
        throw 1;
    }
    if (tokens.size() > 3) {
        cerr << "Ignoring excess arguments for " << tokens[0] << endl; 
        cerr << "usage (example): " << tokens[0] << " A 10000" << endl;
    }
    const string &name = tokens[1];
    const size_t size = atoi(tokens[2].c_str()) * multiplicity;
    mem.named_malloc<T>(name, size);
}

void Sampler::named_offset(const vector<string> &tokens) {
    if (tokens.size() < 4) {
        cerr << "Too few arguments for " << tokens[0] << " (command ignored)" << endl; 
        cerr << "usage (example): " << tokens[0] << " Old 10000 New" << endl;
        throw 1;
    }
    if (tokens.size() > 4) {
        cerr << "Ignoring excess arguments for " << tokens[0] << endl; 
        cerr << "usage (example): " << tokens[0] << " Old 10000 New" << endl;
    }
    const string &oldname = tokens[1];
    const ssize_t offset = atoi(tokens[2].c_str());
    const string &newname = tokens[3];
    mem.named_offset(oldname, offset, newname);
}

void Sampler::named_free(const vector<string> &tokens) {
    if (tokens.size() < 2) {
        cerr << "Too few arguments for " << tokens[0] << " (command ignored)" << endl; 
        cerr << "usage (example): " << tokens[0] << " A" << endl;
        throw 1;
    }
    if (tokens.size() > 2) {
        cerr << "Ignoring excess arguments for " << tokens[0] << endl; 
        cerr << "usage (example): " << tokens[0] << " A" << endl;
    }
    const string &name = tokens[1];
    mem.named_free(name);
}

void Sampler::add_call(const vector<string> &tokens) {
    const string &routine = tokens[0];
    if (signatures.find(routine) == signatures.end()) {
        cerr << "Uknown kernel: " << routine << " (call ignored)" << endl;
        return;
    }
    const Signature &signature = signatures[routine];
    try {
        CallParser callparser(tokens, signature, mem);
        callparsers.push_back(callparser);
    } catch (...) {
        // callparser initialization failed
        // (failure already reported)
    }
}

void Sampler::go() {
    size_t ncalls = callparsers.size();
    KernelCall *calls = new KernelCall[ncalls];

    for (size_t i = 0; i < ncalls; i++)
        calls[i] = callparsers[i].get_call();

#ifdef PAPI
    sample(calls, ncalls, &counters[0], counters.size());
#else
    sample(calls, ncalls);
#endif

    for (size_t i = 0; i < ncalls; i++) {
        cout << calls[i].rdtsc;
#ifdef PAPI
        for (size_t j = 0; j < counters.size(); j++)
            cout << "\t" << call[i].counters[j];
#endif
        cout << endl;
    }

    delete [] calls;
    callparsers.clear();
    mem.static_reset();
}

void Sampler::add_signature(const Signature &signature){
    signatures[signature.name] = signature;
}

void Sampler::start() {
    while (!cin.eof()) {
        // read the next line
        string line;
        getline(cin, line);

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
        if (command == "go")
            go();
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
        else if (command == "offset")
            named_offset(tokens);
        else if (command == "free")
            named_free(tokens);
        else
            // check for kernel call
            add_call(tokens);
    }
    go();
}

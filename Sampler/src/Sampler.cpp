#include "Sampler.hpp"

#include <stdlib.h>
#include <iostream>
#include <sstream>
#include <iterator>

#include CFG_H
#include "sample.h"

using namespace std;

void Sampler::set_counters(vector<string> &tokens) {
#ifdef PAPI
    size_t ncounters = tokens.size() - 1;
    int maxcounters = PAPI_num_counters();
    if (ncounters > maxcounters) {
        cerr << "Too many counters specified: given " << ncounters;
        cerr << " maximum " << maxcounters << " (truncating counter list)" << endl;
        ncounters = maxcounters;
    }
    counters.resize(0);
    for (size_t i = 0; i < ncounters; i++) {
        int code;
        int check = PAPI_event_name_to_code(tokens[i + 1].c_str(), &code)
        if (check == PAPI_OK)
            counters.push_back(code);
        else if (check == PAPI_ENOTPRESET)
            cerr << "Counter unknown: " << tokens[i + 1] << " (counter ignored)" << endl;
        else if (check == PAPI_ENOEVNT)
            cerr << "Counter unavailable: " << tokens[i + 1] << " (counter ignored)" << endl;
    }
#else
    cerr << "PAPI support not enabled (instruction ignored)" << endl;
#endif
}

template <typename T>
void Sampler::named_malloc(vector<string> &tokens, size_t multiplicity=1) {
    string &name = tokens[1];
    size_t size = atoi(tokens[2].c_str()) * multiplicity;
    mem.named_malloc<T>(name, size);
}

void Sampler::named_offset(vector<string> &tokens) {
    string &oldname = tokens[1];
    ssize_t offset = atoi(tokens[2].c_str());
    string &newname = tokens[3];
    mem.named_offset(oldname, offset, newname);
}

void Sampler::named_free(vector<string> &tokens) {
    string &name = tokens[1];
    mem.named_free(name);
}

void Sampler::add_call(vector<string> &tokens) {
    string &routine = tokens[0];
    if (signatures.find(routine) == signatures.end()) {
        cerr << "Uknown kernel: " << routine << " (call ignored)" << endl;
        return;
    }
    Signature &signature = signatures[routine];
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
}

void Sampler::add_signature(Signature signature){
    signatures[signature.name] = signature;
}

void Sampler::start() {
    while (!cin.eof()) {
        // read and tokenize line
        string line;
        getline(cin, line);
        istringstream iss(line);
        vector<string> tokens;
        copy(istream_iterator<string>(iss), istream_iterator<string>(), back_inserter(tokens));
        if (tokens.size() == 0)
            continue;
        // check for special commands
        string &command = tokens[0];
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
            add_call(tokens);
    }
}

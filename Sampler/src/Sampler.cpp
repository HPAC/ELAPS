#include "Sampler.hpp"

#include <stdlib.h>
#include <iostream>
#include <sstream>
#include <iterator>

#include CFG_H
#include "sample.h"

using namespace std;

void Sampler::named_malloc(vector<string> &tokens) {
    string &name = tokens[1];
    size_t size = atoi(tokens[2].c_str());
    mem.named_malloc(name, size);
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
            named_malloc(tokens);
        else if (command == "offset")
            named_offset(tokens);
        else if (command == "free")
            named_free(tokens);
        else
            add_call(tokens);
    }
}

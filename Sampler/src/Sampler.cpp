#include "Sampler.hpp"

#include <cstdlib>
#include <cstring>
#include <iostream>
#include <sstream>
#include <iterator>
#include <complex>

#ifdef PAPI_ENABLED
#include <papi.h>
#endif

#include CFG_H
#include "sample.h"

using namespace std;

////////////////////////////////////////////////////////////////////////////////
// Command: set PAPI counters                                                 //
////////////////////////////////////////////////////////////////////////////////

void Sampler::set_counters(const vector<string> &tokens) {
#ifdef PAPI_ENABLED
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

        // check if combination is valid
        if (PAPI_start_counters(&counters[0], counters.size()) == PAPI_OK) {
            long long counts[counters.size()];
            PAPI_stop_counters(counts, counters.size());
        } else {
            counters.pop_back();
            cerr << "Could not add " << tokens[i + 1] << " (counter ignored)" << endl;
        }
    }
#else
    cerr << "PAPI support not enabled (command ignored)" << endl;
#endif
}

////////////////////////////////////////////////////////////////////////////////
// Commands: OpenMP regions                                                   //
////////////////////////////////////////////////////////////////////////////////

void Sampler::omp_start(const vector<string>&tokens) {
#ifdef OPENMP_ENABLED
    if (tokens.size() > 1)
        cerr << "Ignoring arguments for " << tokens[0] << endl;
    if (omp_active) {
        cerr << "Implicitly ending last parallel region, starting a new one" << endl;
        omp_end(vector<string>());
    }
    omp_active = true;
#else
    cerr << "OpenMP support not enabled (command ignored)" << endl;
#endif
}

void Sampler::omp_end(const vector<string>&tokens) {
#ifdef OPENMP_ENABLED
    if (tokens.size() > 1)
        cerr << "Ignoring arguments for " << tokens[0] << endl;
    if (!omp_active) {
        cerr << "Not in parallel region (comand ignored)" << endl;
        return;
    }
    omp_active = false;
    if (!callparsers.empty())
        callparsers.back().omp_active = true;
#else
    cerr << "OpenMP support not enabled (command ignored)" << endl;
#endif
}

////////////////////////////////////////////////////////////////////////////////
// Commands: Handling named variables                                         //
////////////////////////////////////////////////////////////////////////////////

template <typename T>
void Sampler::named_malloc(const vector<string> &tokens) {
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
    const ssize_t size = atol(tokens[2].c_str());

    // variable must not exist yet
    if (mem.named_exists(name)) {
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
    if (size < 0) {
        cerr << "Cannot allocate variable of negative size " << size << " (command ignored)" << endl;
        return;
    }

    // malloc the variabel
    mem.named_malloc<T>(name, size);
}

template <typename T>
void Sampler::named_offset(const vector<string> &tokens) {
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
    const ssize_t offset = atol(tokens[2].c_str());
    const string &newname = tokens[3];

    // oldname must exist
    if (!mem.named_exists(oldname)) {
        cerr << "Unknown variable: " << oldname << " (command ignored)" << endl;
        return;
    }
    // TODO: check offset conversion errors
    // newname must not exist yet
    if (mem.named_exists(newname)) {
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

////////////////////////////////////////////////////////////////////////////////
// Command: Add a call                                                        //
////////////////////////////////////////////////////////////////////////////////

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
#ifdef OPENMP_ENABLED
        callparser.omp_active = omp_active;
#endif 
        callparsers.push_back(callparser);
    } catch (CallParserException &e) {
        // the call could not be parserd
        // (failure already reported)
    }
}

////////////////////////////////////////////////////////////////////////////////
// Command: Process the current calls                                         //
////////////////////////////////////////////////////////////////////////////////

void Sampler::go(const vector<string> &tokens) {
    // end parallel region if active
#ifdef OPENMP_ENABLED
    if (omp_active) {
        cerr << "Implicitly ending last parallel region" << endl;
        omp_end(vector<string>());
    }
#endif

    size_t ncalls = callparsers.size();
    KernelCall *calls = new KernelCall[ncalls];

    // construct KernelCalls (C structs)
    for (size_t i = 0; i < ncalls; i++)
        calls[i] = callparsers[i].get_call();

    // run measurements
#ifdef PAPI_ENABLED
    sample(calls, ncalls, &counters[0], counters.size());
#else
    sample(calls, ncalls);
#endif

    // print results
    for (size_t i = 0; i < ncalls; i++) {
        CallParser &callparser = callparsers[i];

#ifdef OPENMP_ENABLED
        if (callparser.omp_active)
            // part of a parallel region
            continue;
#endif

        // cycle counter
        cout << calls[i].cycles;

#ifdef PAPI_ENABLED
        // papi counters
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

////////////////////////////////////////////////////////////////////////////////
// Add signatures to the sampler                                              //
////////////////////////////////////////////////////////////////////////////////
void Sampler::print(const vector<string> &tokens) {
    ostringstream text;
    copy(tokens.begin() + 1, tokens.end(), ostream_iterator<string>(text, " "));
    cout << text.str() << endl;
}

void Sampler::info(const vector<string> &tokens) {
    // require 1 argument: kernel name
    if (tokens.size() < 2) {
        cerr << "No argument for " << tokens[0] << " (command ignored)" << endl;
        cerr << "usage (exmaple): " << tokens[0] << " dgemm" << endl;
        return;
    }
    if (tokens.size() > 2) {
        cerr << "Ignoring excess arguments for " << tokens[0] << endl; 
        cerr << "usage (example): " << tokens[0] << " dgemm" << endl;
    }

    const string &routine = tokens[1];

    // catch unknown routines
    if (signatures.find(routine) == signatures.end()) {
        cerr << "Uknown kernel: " << routine << " (command ignored)" << endl;
        return;
    }

    // print <routine name>(
    cerr << routine << "(";

    // print the signatue for the routine
    const Signature &signature = signatures[routine];
    const size_t argc = signature.arguments.size();
    for (unsigned char i = 1; i < argc; i++) {
        switch (signature.arguments[i]) {
            case CHARP:
                cerr << "char *";
                break;
            case INTP:
                cerr << "int *";
                break;
            case FLOATP:
                cerr << "float *";
                break;
            case DOUBLEP:
                cerr << "double *";
                break;
            case VOIDP:
                cerr << "void *";
                break;
            default:
                break;
        }
        if (i + 1 < argc)
            cerr << ", ";
    }

    // print );
    cerr << ");" << endl;
}

void Sampler::add_signature(const Signature &signature) {
    signatures[signature.name] = signature;
}

////////////////////////////////////////////////////////////////////////////////
// Sampler main loop                                                          //
////////////////////////////////////////////////////////////////////////////////

void Sampler::start() {
    // special commands
    map<string, void (Sampler:: *)(const vector<string> &)> commands;
    commands["set_counters"] = &Sampler::set_counters;
    commands["{omp"] = &Sampler::omp_start;
    commands["}"] = &Sampler::omp_end;
    commands["malloc"] = &Sampler::named_malloc<char>;
    commands["imalloc"] = &Sampler::named_malloc<int>;
    commands["smalloc"] = &Sampler::named_malloc<float>;
    commands["dmalloc"] = &Sampler::named_malloc<double>;
    commands["cmalloc"] = &Sampler::named_malloc<complex<float> >;
    commands["zmalloc"] = &Sampler::named_malloc<complex<double> >;
    commands["offset"] = &Sampler::named_offset<char>;
    commands["ioffset"] = &Sampler::named_offset<int>;
    commands["soffset"] = &Sampler::named_offset<float>;
    commands["doffset"] = &Sampler::named_offset<double>;
    commands["coffset"] = &Sampler::named_offset<complex<float> >;
    commands["zoffset"] = &Sampler::named_offset<complex<double> >;
    commands["free"] = &Sampler::named_free;
    commands["go"] = &Sampler::go;
    commands["info"] = &Sampler::info;
    commands["print"] = &Sampler::print;

    // default: not parallel
#ifdef OPENMP_ENABLED
    omp_active = false;
#endif

    // read stdin by lines
    string line;
    while (getline(cin, line)) {

        // clear comments
        line = line.substr(0, line.find_first_of("#"));

        // ignore empty lines
        if (line.size() == 0)
            continue;

        // remove leading spaces
        line = line.substr(line.find_first_not_of(" \t\n\v\f\r"));

        // ignore empty lines
        if (line.size() == 0)
            continue;

        // tokenize line
        vector<string> tokens;
        istringstream iss(line);
        copy(istream_iterator<string>(iss), istream_iterator<string>(), back_inserter(tokens));

        // check for commands
        map<string, void (Sampler:: *)(const vector<string> &)>::iterator command = commands.find(tokens[0]);
        if (command != commands.end())
            (this->*(command->second))(tokens);
        else
            add_call(tokens);
    }

    // process remaining calls
    go(vector<string>());
}

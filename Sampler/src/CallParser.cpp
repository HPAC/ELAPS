#include "CallParser.hpp"

#include <iostream>

#include <ctype.h>
#include <stdlib.h>

using namespace std;

CallParser::CallParser(vector<string> &tokens, Signature &signature, MemoryManager &mem)
: tokens(tokens), signature(&signature), mem(&mem)
{ 
    if (tokens.size() < signature.arguments.size()) {
        cerr << "Too few arguments for kernel " << tokens[0];
        cerr << ": given " << (tokens.size() - 1);
        cerr << " expecing " << (signature.arguments.size() - 1) << " (call ignored)" << endl;
        throw 1;
    }
    if (tokens.size() > signature.arguments.size()) {
        cerr << "Ignoring excess arguments for kernel " << tokens[0];
        cerr << ": given " << (tokens.size() - 1);
        cerr << " expecing " << (signature.arguments.size() - 1) << endl;
    }
    register_args();
}

CallParser::~CallParser() {
}

void CallParser::register_charp(char i) {
    string &val = tokens[i];
    ids[i] = mem->static_register(val.c_str(), val.size() + 1);
}

void CallParser::register_intp(char i) {
    string &val = tokens[i];
    if (val[0] == '[') {
        size_t closing = val.find_first_not_of("0123456789", 1);
        if (closing != val.size() - 1 || val[closing] != ']') {
            cout << "Invalid or incomplete memory size specification for argument " << i << ": " << val << " (call ignored)" << endl;
            throw i;
        }
        memtypes[i] = DYNAMIC;
        size_t size = atoi(val.c_str() + 1);
        ids[i] = mem->dynamic_register(size * sizeof(int));
    } else if (isalpha(val[0])) {
        if (!mem->named_exists(val)) {
            cout << "Unknown variable: " << val << " (call ignored)" << endl;
            throw i;
        }
        memtypes[i] = NAMED;
    } else {
        memtypes[i] = STATIC;
        // TODO: check syntax
        int ival = atoi(val.c_str());
        ids[i] = mem->static_register(&ival, sizeof(int));
    }
}

void CallParser::register_floatp(char i) {
    string &val = tokens[i];
    if (val[0] == '[') {
        size_t closing = val.find_first_not_of("0123456789", 1);
        if (closing != val.size() - 1 || val[closing] != ']') {
            cout << "Invalid or incomplete memory size specification for argument " << i << ": " << val << " (call ignored)" << endl;
            throw i;
        }
        memtypes[i] = DYNAMIC;
        size_t size = atoi(val.c_str() + 1);
        ids[i] = mem->dynamic_register(size * sizeof(float));
    } else if (isalpha(val[0])) {
        if (!mem->named_exists(val)) {
            cout << "Unknown variable: " << val << " (call ignored)" << endl;
            throw i;
        }
        memtypes[i] = NAMED;
    } else {
        memtypes[i] = STATIC;
        // TODO: check syntax
        float ival = atof(val.c_str());
        ids[i] = mem->static_register(&ival, sizeof(float));
    }
}

void CallParser::register_doublep(char i) {
    string &val = tokens[i];
    if (val[0] == '[') {
        size_t closing = val.find_first_not_of("0123456789", 1);
        if (closing != val.size() - 1 || val[closing] != ']') {
            cout << "Invalid or incomplete memory size specification for argument " << i << ": " << val << " (call ignored)" << endl;
            throw i;
        }
        memtypes[i] = DYNAMIC;
        size_t size = atoi(val.c_str() + 1);
        ids[i] = mem->dynamic_register(size * sizeof(double));
    } else if (isalpha(val[0])) {
        if (!mem->named_exists(val)) {
            cout << "Unknown variable: " << val << " (call ignored)" << endl;
            throw i;
        }
        memtypes[i] = NAMED;
    } else {
        memtypes[i] = STATIC;
        // TODO: check syntax
        double ival = atof(val.c_str());
        ids[i] = mem->static_register(&ival, sizeof(double));
    }
}

void CallParser::register_voidp(char i) {
    string &val = tokens[i];
    if (val[0] == '[') {
        size_t closing = val.find_first_not_of("0123456789", 1);
        if (closing != val.size() - 1 || val[closing] != ']') {
            cout << "Invalid or incomplete memory size specification for argument " << i << ": " << val << " (call ignored)" << endl;
            throw i;
        }
        memtypes[i] = DYNAMIC;
        size_t size = atoi(val.c_str() + 1);
        ids[i] = mem->dynamic_register(size);
    } else if (isalpha(val[0])) {
        if (!mem->named_exists(val)) {
            cout << "Unknown variable: " << val << " (call ignored)" << endl;
            throw i;
        }
        memtypes[i] = NAMED;
    } else {
        // static undefined for void*
        throw i;
    }
}

void CallParser::register_args() {
    size_t argc = signature->arguments.size();
    mem->dynamic_newcall();
    memtypes.resize(argc);
    ids.resize(argc);
    for (char i = 1; i < argc; i++)
        switch (signature->arguments[i]) {
            case CHARP:
                register_charp(i);
                break;
            case INTP:
                register_intp(i);
                break;
            case FLOATP:
                register_floatp(i);
                break;
            case DOUBLEP:
                register_doublep(i);
                break;
            case VOIDP:
                register_voidp(i);
                break;
        }
}


KernelCall CallParser::get_call() {
    KernelCall call;
    call.argc = signature->arguments.size();
    call.argv[0] = signature->function;
    for (char i = 1; i < call.argc; i++)
        switch (memtypes[i]) {
            case STATIC:
                call.argv[i] = mem->static_get(ids[i]);
                break;
            case NAMED:
                call.argv[i] = mem->named_get(tokens[i]);
                break;
            case DYNAMIC:
                call.argv[i] = mem->dynamic_get(ids[i]);
                break;
        }
    return call;
}

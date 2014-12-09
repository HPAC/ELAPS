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

size_t get_type_size(ArgType arg) {
    switch (arg) {
        case CHARP:
            return sizeof(char);
        case INTP:
            return sizeof(int);
        case FLOATP:
            return sizeof(float);
        case DOUBLEP:
            return sizeof(double);
        case VOIDP:
            return 1;
    }
}

void CallParser::register_args() {
    size_t argc = signature->arguments.size();
    mem->dynamic_newcall();
    memtypes.resize(argc);
    ids.resize(argc);
    for (char i = 1; i < argc; i++) {
        ArgType &arg = signature->arguments[i];
        size_t type_size = get_type_size(arg);
        string &val = tokens[i];
        if (arg == CHARP) {
            // string
            memtypes[i] = STATIC;
            ids[i] = mem->static_register(val.c_str(), val.size() + 1);
        } else if (val[0] == '[') {
            // dynamic memory: [1234]
            size_t closing = val.find_first_not_of("0123456789", 1);
            if (closing != val.size() - 1 || val[closing] != ']') {
                cout << "Invalid or incomplete memory size specification for argument " << i << ": " << val << " (call ignored)" << endl;
                throw i;
            }
            memtypes[i] = DYNAMIC;
            size_t size = atoi(val.c_str() + 1);
            switch (arg) {
                case INTP:
                    ids[i] = mem->dynamic_register<int>(size);
                    break;
                case FLOATP:
                    ids[i] = mem->dynamic_register<float>(size);
                    break;
                case DOUBLEP:
                    ids[i] = mem->dynamic_register<double>(size);
                    break;
                case VOIDP:
                    ids[i] = mem->dynamic_register<char>(size);
                    break;
            }
        } else if (isalpha(val[0])) {
            // named variable
            if (!mem->named_exists(val)) {
                cout << "Unknown variable: " << val << " (call ignored)" << endl;
                throw i;
            }
            memtypes[i] = NAMED;
        } else {
            // static (constant) variables, comma separated
            if (arg == VOIDP) {
                cerr << "Cannot parse to void:" << val << " (call ignored)" << endl;
                throw i;
            }
            memtypes[i] = STATIC;
            int type_size = get_type_size(arg);
            vector<char> data;
            size_t pos = 0;
            while (pos != val.npos) {
                // read comma separated value into temporary list
                char *str = (char *) val.c_str() + pos;
                data.resize(data.size() + type_size);
                void *datap = (void *) &data[data.size() - type_size];
                switch (arg) {
                    case INTP:
                        *((int *) datap) = atoi(val.c_str());
                        break;
                    case FLOATP:
                        *((float *) datap) = atof(val.c_str());
                        break;
                    case DOUBLEP:
                        *((double *) datap) = atof(val.c_str());
                        break;
                }
                pos = val.find_first_of(',', pos);
                pos += (val[pos] == ',');
            }
            ids[i] = mem->static_register((void *) &data[0], data.size());
        }
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

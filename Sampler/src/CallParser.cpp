#include "CallParser.hpp"

#include <iostream>

#include <cstdlib>
#include <cctype>

using namespace std;

////////////////////////////////////////////////////////////////////////////////
// Initialize from token list                                                 //
////////////////////////////////////////////////////////////////////////////////

CallParser::CallParser(vector<string> &tokens, Signature &signature, MemoryManager &mem)
: tokens(tokens), signature(&signature), mem(&mem)
{ 
    // check for too few arguments
    if (tokens.size() < signature.arguments.size()) {
        cerr << "Too few arguments for kernel " << tokens[0];
        cerr << ": given " << (tokens.size() - 1);
        cerr << " expecing " << (signature.arguments.size() - 1) << " (call ignored)" << endl;
        throw 1;
    }
    // check for too many arguments (warning only)
    if (tokens.size() > signature.arguments.size()) {
        cerr << "Ignoring excess arguments for kernel " << tokens[0];
        cerr << ": given " << (tokens.size() - 1);
        cerr << " expecing " << (signature.arguments.size() - 1) << endl;
    }
    // process arguments
    register_args();
}

////////////////////////////////////////////////////////////////////////////////
// Read 1 static value from string                                            //
////////////////////////////////////////////////////////////////////////////////

template <> int CallParser::read_static<int>(char *str) {
    return atoi(str);
}

template <> float CallParser::read_static<float>(char *str) {
    return (float) atof(str);
}

template <> double CallParser::read_static<double>(char *str) {
    return atof(str);
}

////////////////////////////////////////////////////////////////////////////////
// Register static variable (list)                                            //
////////////////////////////////////////////////////////////////////////////////

template <typename T> void CallParser::register_static(char i) {
    string &val = tokens[i];
    vector<T> data;
    size_t pos = 0;
    while (pos != val.npos) {
        // read comma separated list 
        pos += (val[pos] == ',');
        char *str = (char *) val.c_str() + pos;
        data.push_back(read_static<T>(str));
        pos = val.find_first_of(',', pos);
    }
    memtypes[i] = STATIC;
    ids[i] = mem->static_register((void *) &data[0], data.size() * sizeof(T));
}

// no static initialization for void *
template <> void CallParser::register_static<void>(char i) {
    string &val = tokens[i];
    cerr << "Cannot parse to void:" << val << " (call ignored)" << endl;
    throw 1;
}

////////////////////////////////////////////////////////////////////////////////
// Register named variabes                                                    //
////////////////////////////////////////////////////////////////////////////////

template <typename T> void CallParser::register_named(char i) {
    string &val = tokens[i];
    if (!mem->named_exists(val)) {
        cout << "Unknown variable: " << val << " (call ignored)" << endl;
        throw i;
    }
    memtypes[i] = NAMED;
}

////////////////////////////////////////////////////////////////////////////////
// Register dynamic variabes                                                  //
////////////////////////////////////////////////////////////////////////////////

template <typename T> void CallParser::register_dynamic(char i) {
    string &val = tokens[i];
    size_t closing = val.find_first_not_of("0123456789", 1);
    if (closing != val.size() - 1 || val[closing] != ']') {
        cout << "Invalid or incomplete memory size specification for argument " << i << ": " << val << " (call ignored)" << endl;
        throw i;
    }
    memtypes[i] = DYNAMIC;
    size_t size = atoi(val.c_str() + 1);
    ids[i] = mem->dynamic_register<T>(size);
}

////////////////////////////////////////////////////////////////////////////////
// Register single argument                                                   //
////////////////////////////////////////////////////////////////////////////////

template <typename T> void CallParser::register_arg(char i) {
    string &val = tokens[i];
    if (val[0] == '[')
        register_dynamic<T>(i);
    else if (isalpha(val[0]))
        register_named<T>(i);
    else
        register_static<T>(i);
}

// all char * are treated as static
template <> void CallParser::register_arg<char>(char i) {
    string &val = tokens[i];
    memtypes[i] = STATIC;
    ids[i] = mem->static_register(val.c_str(), val.size() + 1);
}

////////////////////////////////////////////////////////////////////////////////
// Register all arguments                                                     //
////////////////////////////////////////////////////////////////////////////////

void CallParser::register_args() {
    size_t argc = signature->arguments.size();
    mem->dynamic_newcall();
    memtypes.resize(argc);
    ids.resize(argc);
    for (char i = 1; i < argc; i++)
        switch (signature->arguments[i]) {
            case CHARP:
                register_arg<char>(i);
                break;
            case INTP:
                register_arg<int>(i);
                break;
            case FLOATP:
                register_arg<float>(i);
                break;
            case DOUBLEP:
                register_arg<double>(i);
                break;
            case VOIDP:
                register_arg<void>(i);
                break;
        }
}

////////////////////////////////////////////////////////////////////////////////
// Produce call                                                               //
////////////////////////////////////////////////////////////////////////////////

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

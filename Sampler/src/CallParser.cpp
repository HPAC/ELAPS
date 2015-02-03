#include "CallParser.hpp"

#include <iostream>

#include <cstdlib>
#include <cctype>

using namespace std;

////////////////////////////////////////////////////////////////////////////////
// Initialize from token list                                                 //
////////////////////////////////////////////////////////////////////////////////

CallParser::CallParser(const vector<string> &tokens, const Signature &signature, MemoryManager &mem)
: mem(&mem), signature(&signature), tokens(tokens)
{ 
    // check for too few arguments
    if (tokens.size() < signature.arguments.size()) {
        cerr << "Too few arguments for kernel " << tokens[0];
        cerr << ": given " << (tokens.size() - 1);
        cerr << " expecing " << (signature.arguments.size() - 1) << " (call ignored)" << endl;
        throw CallParserException();
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

template <> int CallParser::read_static<int>(const char *str) const {
    // TODO: check for conversion errors
    return atoi(str);
}

template <> float CallParser::read_static<float>(const char *str) const {
    // TODO: check for conversion errors
    return (float) atof(str);
}

template <> double CallParser::read_static<double>(const char *str) const {
    // TODO: check for conversion errors
    return atof(str);
}

////////////////////////////////////////////////////////////////////////////////
// Register static variable (list)                                            //
////////////////////////////////////////////////////////////////////////////////

template <typename T> void CallParser::register_static(unsigned char i) {
    const string &val = tokens[i];
    vector<T> data;

    // read comma separated list into array
    size_t pos = 0;
    while (pos != val.npos) {
        // skip ,
        pos += (val[pos] == ',');

        // read value
        const char *str = val.c_str() + pos;
        data.push_back(read_static<T>(str));

        // skip to next , (or end)
        pos = val.find_first_of(',', pos);
    }

    // register variable
    memtypes[i] = STATIC;
    ids[i] = mem->static_register((void *) &data[0], data.size() * sizeof(T));
}

template <> void CallParser::register_static<void>(unsigned char i) {
    // cannot statically initialize void *
    cerr << "Cannot parse to void:" << tokens[i] << " (call ignored)" << endl;
    throw CallParserException();
}

////////////////////////////////////////////////////////////////////////////////
// Register named variabes                                                    //
////////////////////////////////////////////////////////////////////////////////

template <typename T> void CallParser::register_named(unsigned char i) {
    const string &val = tokens[i];

    // check variable existence
    if (!mem->named_exists(val)) {
        cout << "Unknown variable: " << val << " (call ignored)" << endl;
        throw CallParserException();
    }

    // named variables are processed in get_call()
    memtypes[i] = NAMED;
}

////////////////////////////////////////////////////////////////////////////////
// Register dynamic variabes                                                  //
////////////////////////////////////////////////////////////////////////////////

template <typename T> void CallParser::register_dynamic(unsigned char i) {
    // We know the token starts with [
    const string &val = tokens[i];

    // make sure it contains only numbers and ens with ]
    const size_t closing = val.find_first_not_of("0123456789", 1);
    if (closing != val.size() - 1 || val[closing] != ']') {
        cout << "Invalid or incomplete memory size specification: " << val << " (call ignored)" << endl;
        throw CallParserException();
    }

    // register memory accordingly
    memtypes[i] = DYNAMIC;
    const size_t size = atoi(val.c_str() + 1);
    ids[i] = mem->dynamic_register<T>(size);
}

////////////////////////////////////////////////////////////////////////////////
// Register single argument                                                   //
////////////////////////////////////////////////////////////////////////////////

template <typename T> void CallParser::register_arg(unsigned char i) {
    const string &val = tokens[i];
    if (val[0] == '[')
        // dynamic memory is requested as [size]
        register_dynamic<T>(i);
    else if (isalpha(val[0]))
        // named variables start with a letter
        register_named<T>(i);
    else
        // anything else is parsed to static
        register_static<T>(i);
}

// all char * are treated as static
template <> void CallParser::register_arg<char>(unsigned char i) {
    const string &val = tokens[i];

    // register the string straight from the token
    memtypes[i] = STATIC;
    ids[i] = mem->static_register(val.c_str(), val.size() + 1);
}

////////////////////////////////////////////////////////////////////////////////
// Register all arguments                                                     //
////////////////////////////////////////////////////////////////////////////////

void CallParser::register_args() {
    // make space for the call
    const size_t argc = signature->arguments.size();
    mem->dynamic_newcall();
    memtypes.resize(argc);
    ids.resize(argc);

    // process arguments by expected type
    for (unsigned char i = 1; i < argc; i++)
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
            default:
                break;
        }
}

////////////////////////////////////////////////////////////////////////////////
// Set omp_active                                                             //
////////////////////////////////////////////////////////////////////////////////

#ifdef OPENMP_ENABLED
void CallParser::set_omp_active(bool active) {
    omp_active = active;
}
#endif

////////////////////////////////////////////////////////////////////////////////
// Produce call                                                               //
////////////////////////////////////////////////////////////////////////////////

KernelCall CallParser::get_call() const {
    KernelCall call;

    // set up argument count and function pointer
    call.argc = signature->arguments.size();
    call.argv[0] = signature->function;

    // get the argument pointers from the MemoryManager
    for (unsigned char i = 1; i < call.argc; i++)
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

#ifdef OPENMP_ENABLED
    call.parallel = omp_active;
#endif

    return call;
}

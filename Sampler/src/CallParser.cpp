#include "CallParser.hpp"

#include CFG_H

#include <iostream>

#include <cstdlib>
#include <cctype>

using namespace std;

CallParser::CallParser(const vector<string> &tokens_, const Signature &signature_, MemoryManager &mem_)
: mem(&mem_), signature(&signature_), tokens(tokens_)
{
    const size_t nargs = signature->arguments.size();
    const size_t ntokens = tokens.size();
    // check for too few arguments
    if (ntokens < nargs) {
        cerr << "Too few arguments for kernel " << tokens[0];
        cerr << ": given " << ntokens - 1;
        cerr << " expecting " << nargs - 1 << " (call ignored)" << endl;
        throw CallParser::CallParserException();
    }
    // check for too many arguments (warning only)
    if (ntokens > nargs) {
        cerr << "Ignoring excess arguments for kernel " << tokens[0];
        cerr << ": given " << ntokens - 1;
        cerr << " expecting " << nargs - 1 << endl;
    }

    // process arguments
    register_args();
}

/** Explicit \ref read_static instantiation for `int`. */
template <> int CallParser::read_static<int>(const char *str) const {
    // TODO: check for conversion errors
    return static_cast<int>(atol(str));
}

/** Explicit \ref read_static instantiation for `float`. */
template <> float CallParser::read_static<float>(const char *str) const {
    // TODO: check for conversion errors
    return static_cast<float>(atof(str));
}

/** Explicit \ref read_static instantiation for `double`. */
template <> double CallParser::read_static<double>(const char *str) const {
    // TODO: check for conversion errors
    return atof(str);
}

template <typename T> void CallParser::register_static(unsigned char argid) {
    const string &val = tokens[argid];
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
    memtypes[argid] = STATIC;
    ids[argid] = mem->static_register(static_cast<void *>(&data[0]), data.size() * sizeof(T));
}

/** Explicit \ref register_static instantiation for `void`.
 * Since we cannot parse to `void`, throw an Exception.
 */
template <> void CallParser::register_static<void>(unsigned char i) {
    // cannot statically initialize void *
    cerr << "Cannot parse to void:" << tokens[i] << " (call ignored)" << endl;
    throw CallParser::CallParserException();
}

void CallParser::register_named(unsigned char i) {
    const string &val = tokens[i];

    // check variable existence
    if (!mem->named_exists(val)) {
        cout << "Unknown variable: " << val << " (call ignored)" << endl;
        throw CallParser::CallParserException();
    }

    // named variables are processed in get_call()
    memtypes[i] = NAMED;
}

template <typename T> void CallParser::register_dynamic(unsigned char i) {
    // We know the token starts with [
    const string &val = tokens[i];

    // make sure it contains only numbers and ens with ]
    const size_t closing = val.find_first_not_of("0123456789", 1);
    if (closing != val.size() - 1 || val[closing] != ']') {
        cout << "Invalid or incomplete memory size specification: " << val << " (call ignored)" << endl;
        throw CallParser::CallParserException();
    }

    // register memory accordingly
    memtypes[i] = DYNAMIC;
    const size_t size = static_cast<size_t>(atol(val.c_str() + 1));
    ids[i] = mem->dynamic_register<T>(size);
}

template <typename T> void CallParser::register_arg(unsigned char i) {
    const string &val = tokens[i];
    if (val[0] == '[')
        // dynamic memory is requested as [size]
        register_dynamic<T>(i);
    else if (isalpha(val[0]))
        // named variables start with a letter
        register_named(i);
    else
        // anything else is parsed to static
        register_static<T>(i);
}

/** Explicit \ref register_arg instantiation for `char`.
 * `char` are always parsed as Static Memory variables.
 */
template <> void CallParser::register_arg<char>(unsigned char i) {
    const string &val = tokens[i];

    // register the string straight from the token
    memtypes[i] = STATIC;
    ids[i] = mem->static_register(val.c_str(), val.size() + 1);
}

void CallParser::register_args() {
    // make space for the call
    const size_t argc = signature->arguments.size();
    mem->dynamic_newcall();
    memtypes.resize(argc);
    ids.resize(argc);

    // process arguments by expected type
    for (unsigned char i = 1; i < argc; i++)
        switch (signature->arguments[i]) {
            case NONE:
            case NAME:
                break;
            case CHARP:
            case CONST_CHARP:
                register_arg<char>(i);
                break;
            case INTP:
            case CONST_INTP:
                register_arg<int>(i);
                break;
            case FLOATP:
            case CONST_FLOATP:
                register_arg<float>(i);
                break;
            case DOUBLEP:
            case CONST_DOUBLEP:
                register_arg<double>(i);
                break;
            case VOIDP:
            case CONST_VOIDP:
                register_arg<void>(i);
                break;
        }
}

KernelCall CallParser::get_call() const {
    KernelCall call;

    // set up argument count and function pointer
    call.argc = static_cast<unsigned char>(signature->arguments.size());
    call.fptr = signature->fptr;

    // get the argument pointers from the MemoryManager
    for (unsigned char i = 1; i < call.argc; i++)
        switch (memtypes[i]) {
            case STATIC:
                call.argv[i - 1] = mem->static_get(ids[i]);
                break;
            case NAMED:
                call.argv[i - 1] = mem->named_get(tokens[i]);
                break;
            case DYNAMIC:
                call.argv[i - 1] = mem->dynamic_get(ids[i]);
                break;
        }

#ifdef OPENMP_ENABLED
    call.parallel = omp_active;
    call.sequential = seq_active;
#endif

    return call;
}

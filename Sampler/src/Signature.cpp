#include "Signature.hpp"

using namespace std;

Signature::Signature(const char *name, void (*fptr)(), const ArgType *args) 
: name(name), fptr(fptr) {
    // first argument type is the name
    arguments.push_back(NAME);

    // add arguments until NONE = \0 (end of input)
    for (size_t i = 0; args[i] != NONE; i++)
        arguments.push_back(args[i]);
}

Signature::Signature() { }

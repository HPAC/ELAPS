#include "Signature.hpp"

using namespace std;

Signature::Signature(const char *name, void *fptr, ArgType *args) 
: name(name), function(fptr) {
    arguments.push_back(NAME);
    for (int i = 0; args[i] != NONE; i++)
        arguments.push_back(args[i]);
}

Signature::Signature() { }


#ifndef SIGNATURE_HPP
#define SIGNATURE_HPP

#include <vector>
#include <string>

enum ArgType { NONE = '\0', NAME, CHARP, INTP, FLOATP, DOUBLEP, VOIDP };

class Signature {
    public:
        std::string name;
        void *function;
        std::vector<ArgType> arguments;

        Signature(const char *name, void *fptr, const ArgType *arguments);
        Signature();
};

#endif /* SIGNATURE_HPP */

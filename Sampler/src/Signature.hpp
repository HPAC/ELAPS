#ifndef SIGNATURE_HPP
#define SIGNATURE_HPP

#include <vector>
#include <string>

/** Types of arguments. */
enum ArgType {
    NONE = '\0', /**< = NULL, signals the end of the argument list. */
    NAME, /**< Kernel name (argument 0). */
    CHARP, /**< `char *`. */
    INTP, /**< `int *`. */
    FLOATP, /**< `float *`. */
    DOUBLEP,  /**< `double *`. */
    VOIDP /**< `void *` (for completeness). */
};

/** Representation of kernel signature with corresponding function pointer. */
class Signature {
    public:
        /** Name of the kernel. */
        std::string name;

        /** Function pointer to the kernel. */
        void (*fptr)();

        /** Argument types. */
        std::vector<ArgType> arguments;

        /** Constructor.
         * Creates the \ref arguments from the raw list of input \p args.
         *
         * \param name  Initial value for \p name.
         * \param fptr  Initial value for \p fptr.
         * \param args  List of arguments, \ref ArgType::NONE terminated.
         */
        Signature(const char *name, void (*fptr)(), const ArgType *args);

        /** Default Destructor */
        Signature();
};

#endif /* SIGNATURE_HPP */

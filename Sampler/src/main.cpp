#include "Sampler.hpp"
#include <cstdlib>

#include CFG_H

extern "C" {
#include KERNEL_H
}

/** Main entry point for executables. */
int main() {
    Sampler sampler;

    // load signatures
    {
        // signature data type
        typedef struct {
            const char *name;
            void *fptr;
            ArgType args[KERNEL_MAX_ARGS];
        } sigstruct;

        // static initialization from an include file
        const sigstruct sigs[] = {
#include SIGS_C_INC
            {""}  // needed to mark the end
        };

        // add signatures to the sampler 1 by 1
        for (size_t i = 0; sigs[i].name[0] != '\0'; i++)
            sampler.add_signature(Signature(sigs[i].name, sigs[i].fptr, sigs[i].args));
    }

    // start the sampler
    sampler.start();

    return EXIT_SUCCESS;
}

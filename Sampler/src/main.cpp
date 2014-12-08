#include "Sampler.hpp"

#include CFG_H

extern "C" {
#include KERNEL_H
}

int main(int argc, char *argv[]) {
    // TODO: argument parsing for PAPI counters
    Sampler sampler;

    // load signatures
    {
        typedef struct {
            const char *name;
            void *fptr;
            ArgType args[KERNEL_MAX_ARGS];
        } sigstruct;
        sigstruct sigs[] = {
#include SIGS_C_INC
            {""}
        };
        for (size_t i = 0; sigs[i].name[0] != '\0'; i++)
            sampler.add_signature(Signature(sigs[i].name, sigs[i].fptr, sigs[i].args));
    }

    sampler.start();
}

#ifndef CALLPARSER_HPP
#define CALLPARSER_HPP

#include <vector>

#include "MemoryManager.hpp"
#include "Signature.hpp"
#include "KernelCall.h"


class CallParser {
    private:
        enum MemType { STATIC, NAMED, DYNAMIC };

        // Associated Memory Manager
        MemoryManager *mem;
        Signature *signature;

        // original tokenized string
        std::vector<std::string> tokens;

        // memory types and location ids
        std::vector<MemType> memtypes;
        std::vector<size_t> ids;

        // registering args with the memory manager
        void register_args();

        void register_charp(char i);
        void register_intp(char i);
        void register_floatp(char i);
        void register_doublep(char i);
        void register_voidp(char i);

    public:
        CallParser(std::vector<std::string> &tokens, Signature &signature, MemoryManager &mem);
        ~CallParser();

        KernelCall get_call();
};

#endif /* CALLPARSER_HPP */

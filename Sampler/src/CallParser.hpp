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
        template <typename T> T read_static(char *str);
        template <typename T> void register_static(char i);
        template <typename T> void register_named(char i);
        template <typename T> void register_dynamic(char i);
        template <typename T> void register_arg(char i);
        void register_args();

    public:
        CallParser(std::vector<std::string> &tokens, Signature &signature, MemoryManager &mem);
        ~CallParser();

        KernelCall get_call();
};

#endif /* CALLPARSER_HPP */

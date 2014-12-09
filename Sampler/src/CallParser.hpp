#ifndef CALLPARSER_HPP
#define CALLPARSER_HPP

#include "MemoryManager.hpp"
#include "Signature.hpp"
#include "KernelCall.h"

#include <vector>
#include <string>

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
        std::vector<std::size_t> ids;

        // registering args with the memory manager
        template <typename T> T read_static(char *str);
        template <typename T> void register_static(unsigned char i);
        template <typename T> void register_named(unsigned char i);
        template <typename T> void register_dynamic(unsigned char i);
        template <typename T> void register_arg(unsigned char i);
        void register_args();

    public:
        CallParser(std::vector<std::string> &tokens, Signature &signature, MemoryManager &mem);

        KernelCall get_call();
};

#endif /* CALLPARSER_HPP */

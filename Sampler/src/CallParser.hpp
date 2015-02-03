#ifndef CALLPARSER_HPP
#define CALLPARSER_HPP

#include "MemoryManager.hpp"
#include "Signature.hpp"
#include "KernelCall.h"

#include <vector>
#include <string>

class CallParserException: public std::exception { };

class CallParser {
    private:
        enum MemType { STATIC, NAMED, DYNAMIC };

        // Associated Memory Manager
        MemoryManager *mem;
        const Signature *signature;

        // original tokenized string
        std::vector<std::string> tokens;

        // memory types and location ids
        std::vector<MemType> memtypes;
        std::vector<std::size_t> ids;

#ifdef OPENMP_ENABLED
        bool omp_active;
#endif

        // registering args with the memory manager
        template <typename T> T read_static(const char *str) const;
        template <typename T> void register_static(unsigned char i);
        template <typename T> void register_named(unsigned char i);
        template <typename T> void register_dynamic(unsigned char i);
        template <typename T> void register_arg(unsigned char i);
        void register_args();

    public:
        CallParser(const std::vector<std::string> &tokens, const Signature &signature, MemoryManager &mem);

#ifdef OPENMP_ENABLED
        void set_omp_active(bool active = true);
#endif

        KernelCall get_call() const;
};

#endif /* CALLPARSER_HPP */

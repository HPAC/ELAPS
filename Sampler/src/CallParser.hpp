#ifndef CALLPARSER_HPP
#define CALLPARSER_HPP

#include "MemoryManager.hpp"
#include "Signature.hpp"
#include "KernelCall.h"

#include <vector>
#include <string>

/** Parser for kernel calls.
 * Parses input lines (tokens), registers memory, and prepares KenrelCall%s for
 * execution.
 */
class CallParser {
    private:

        /** Types of Memory.
         * See also: MemoryManager.
         */
        enum MemType {
            STATIC, /**< Static Memory. */
            NAMED, /**< Named Memory. */
            DYNAMIC /**< Dynamic Memory. */
        };

        /** Memory Manager instance. */
        MemoryManager *mem;

        /** Kernel signature. */
        const Signature *signature;

        /** Original tokenized string. */
        std::vector<std::string> tokens;

        /** Memory type for each argument. */
        std::vector<MemType> memtypes;

        /** Memory ids for Static and Dynamic Memory. */
        std::vector<std::size_t> ids;

        /** Parse \p str as a \p T.
         *
         * \tparam T    Type as which \p str is to be interpreted.
         * \param str   String to be interpreted.
         * \return The parsing result.
         */
        template <typename T> T read_static(const char *str) const;

        /** Register an argument as a Static Memory variable.
         * Parses argument token \p argid as a variable value or a comma
         * separated list of such.  Registers corresponding space in \ref mem's
         * Static Memory.
         *
         * \tparam T    Data type as which to parse the argument token.
         * \param argid Argument number.
         */
        template <typename T> void register_static(unsigned char argid);

        /** Register a Named Memory buffer for an argument.
         * Parses argument token \p argid as a buffer name.  A corresponding
         * Named Memory buffer must exist in \ref mem.
         *
         * \param argid Argument number.
         */
        void register_named(unsigned char argid);

        /** Register a Dynamic Memory buffer for an argument.
         * Parses argument token \p argid as a Dynamic Memory buffer size for
         * elements of type \p T.  Registers corresponding space in \ref mem's
         * Dynamic Memory buffer for this call.
         *
         * \tparam T    Data type of which to reserve space
         * \param argid Argument number.
         */
        template <typename T> void register_dynamic(unsigned char argid);

        /** Register an argument.
         * Determines which type of memory the argument requests for argument
         * \p argid of data type \p T.  `char *` are always parsed as Static
         * Memory.  For the others, the following patters apply
         * | Format       | Memory type |
         * | ------------ | ----------- |
         * | `\[[0-9]+\]` | Dynamic     |
         * | `[A-Z].*`    | Named       |
         * | other        | Named       |
         *
         * \tparam T    Data type of which to reserve space
         * \param argid Argument number.
         */
        template <typename T> void register_arg(unsigned char argid);

        /** Register all call arguments.
         * \ref register_arg is invoked for each argument with the
         * corresponding template type \p T as determined by \ref signature.
         */
        void register_args();

    public:
        /** Custom exception thrown by CallParser%s. */
        class CallParserException: public std::exception { };

#ifdef OPENMP_ENABLED
        /** Is this call in parallel with the next? */
        bool omp_active;
#endif

        /** Constructor.
         *
         * \param tokens    Kernel name + arguments as strings.
         * \param signature Signature corresponding to the kernel.
         * \param mem   The Sampler's MemoryManager.
         */
        CallParser(const std::vector<std::string> &tokens, const Signature &signature, MemoryManager &mem);

        /** Get a corresponding KernelCall.
         * Resolves all argument ids (Static and Dynamic Memory) and names
         * (Named Memory) and sets up a KernelCall for \ref sample.
         *
         * \return The prepared call.
         */
        KernelCall get_call() const;
};

#endif /* CALLPARSER_HPP */

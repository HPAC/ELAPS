#ifndef SAMPLER_HPP
#define SAMPLER_HPP

#include CFG_H
#include "MemoryManager.hpp"
#include "Signature.hpp"
#include "CallParser.hpp"

#include <vector>
#include <map>
#include <string>

/** Main class.
 * This class contains the main control flow.  It reads the input stream,
 * executes the encountered commands and creates the list of calls.
 */
class Sampler {
    private:
        /** Map of kernel names to Signature%s. */
        std::map<const std::string, Signature> signatures;

        /** Central memory management unit. */
        MemoryManager mem;

        /** List of \ref CallParser%s.
         * For each call encountered in `stdin` a CallParser instance is
         * created and added to this list.  Upon `go` (start of sampling), the
         * CallParser%s provide kernel and argument pointers to invoke the
         * kernels as requested.
         */
        std::vector<CallParser> callparsers;

#ifdef OPENMP_ENABLED
        /** Next call is in parallel?
         * If `true`, the next recorded call is executed parallel to the
         * previous.
         */
        bool omp_active;

        /** Next call is sequential in a parallel region?
         * If `true`, the next recorded call is executed sequentially after the
         * previous in a parallel region
         */
        bool seq_active;
#endif

#ifdef PAPI_ENABLED
        /** List of PAPI counter identifiers.
         * The selection of PAPI counters is fixed for each block of sampling
         * executions (each `go` instruction).
         */
        std::vector<int> counters;
#endif

        /** Command `set_counters [` *counter* `[...]]`: Set PAPI counters
         * Set the PAPI counters to be measured.  The event (counter) names are
         * parsed to event codes.  Unknown events or events incompatible with
         * the previously selected set are ignored.
         *
         * Only available when compiled with PAPI enabled.
         *
         * \param tokens    command + arguments: `set_counters [` *counter* `[...]]`
         * - *counter*: A PAPI event name.
         */
        void set_counters(const std::vector<std::string> &tokens);

        /** Command `{omp`: Begin an OpenMP parallel region.
         * Start a new parallel region.  If already in a parallel region, the
         * last region is closed and a new is opened.
         *
         * Only available when compiled with OpenMP enabled.
         *
         * \param tokens    command + arguments: `{omp`
         */
        void omp_start(const std::vector<std::string> &tokens);

        /** Command `{seq`: Begin a sequential region.
         * Start a new sequential region.  If already in a sequential region,
         * the last region is closed and a new is opened.
         *
         * Only available when compiled with OpenMP enabled.
         *
         * \param tokens    command + arguments: `{seq`
         */
        void seq_start(const std::vector<std::string> &tokens);

        /** Command `}`: End an OpenMP parallel or sequential region.
         * End the current parallel or sequential region.  If not in a parallel
         * region, nothing happens.
         *
         * Only available when compiled with OpenMP enabled.
         *
         * \param tokens    command + arguments: `}`
         */
        void region_end(const std::vector<std::string> &tokens);

        /** Command `*malloc` *name size*: allocate a named buffer.
         * Allocates a new named buffer of specified size.  Parses its
         * arguments and invokes \ref MemoryManager::named_malloc.
         *
         * The prefix `*` is handled in \ref start and indicates/corresponds to
         * the data type \p T:
         * | prefix | data type \p T    |
         * | ------ | ----------------- |
         * |        | `char`            |
         * | `i`    | `int`             |
         * | `s`    | `float`           |
         * | `d`    | `double`          |
         * | `c`    | `complex<float>`  |
         * | `z`    | `complex<double>` |
         *
         * \tparam T    data type to be allocated.
         *
         * \param tokens    command + arguments: `*malloc` *name size>*
         * - *name*: A previously unused buffer name, beginning with a letter.
         * - *size*: Number of elements of type \p T to allocate.
         */
        template <typename T> void named_malloc(const std::vector<std::string> &tokens);

        /** Command `*offset` *name offset new_name*: compute offset into a named buffer.
         * Computes an offset into an existing named buffer and assigns it a
         * new buffer name.  There are no size checks.  Parses its arguments
         * and invokes \ref MemoryManager::named_offset.
         *
         * The prefix `*` is handled in \ref start and indicates/corresponds to
         * the data type \p T (see \ref named_malloc)
         *
         * \tparam T    data type to be allocated.
         *
         * \param tokens    command + arguments: `*offset` *name offset new_name*
         * - *name*: A previously allocated named buffer.
         * - *offset*: Number of elements of type \p T from the start of buffer
         *   *name*, where *new_name* shall point.
         * - *new_name*: A previously unused buffer name, beginning with a letter.
         */
        template <typename T> void named_offset(const std::vector<std::string> &tokens);

        /** Command `free` *name*: free a named buffer.
         * Frees a named buffer.  Parses its argument and invokes \ref
         * MemoryManager::named_free.
         *
         * \param tokens    command + arguments: `free` *name*
         * - *name*: A previously allocated named buffer.
         */
        void named_free(const std::vector<std::string> &tokens);

        /** Register a new call.
         * If a \ref signatures contains a Signature for the specified kernel
         * a corresponding CallParser is added to \ref callparsers.
         *
         * \param tokens    kernel name + arguments: *kernel_name* `[` *arg* `[...]]`
         */
        void add_call(const std::vector<std::string> &tokens, bool hidden);

        /** Sample registerd calls.
         * Samples all recorded calls and prints the measurements.  If inside
         * an OpenMP parallel region, the regions is implicitly closed.
         *
         * Each CallParser from \ref callparsers generates a KernelCall
         * instance.  The collection of all instances is passed \ref sample.
         * The obtained measurements are then printed to `stdout`.
         *
         * \param tokens    command + arguments: `go`
         */
        void go(const std::vector<std::string> &tokens);

        /** Command `info` *kernel_name*: Print kernel signature.
         * Print the signature of a kernel.
         *
         * Example:
         *
         *     > info dgemm
         *     dgemm(char *, char *, int *, int *, int *, double *, double *, int *, double *, int *, double *, double *, int *);
         *
         * \param tokens    command + arguments: `info` *kernel_name*
         * - *kernel_name*: Name of a kernel within \ref signatures.
         */
        void info(const std::vector<std::string> &tokens);

        /** Command `print` *text*: Print text to stdout.
         * Print raw text to stdout.
         *
         * Example:
         *
         *     > print Hello, World!
         *     Hello, World!
         *
         * \param tokens    command + arguments: `print` *text*
         * - *text*: Raw text to be printed.
         */
        void print(const std::vector<std::string> &tokens);

    public:
        /** Add a Signature.
         * Adds \p signature to \ref signatures under its kenrels' name.
         *
         * \param signature Signature
         */
        void add_signature(const Signature &signature);

        /** Main loop and entry point.
         * The Sampler main loop reads `stdin` line by line.  Thereby
         * discarding anything following the comment character `#` and empty
         * lines.  The lines are tokenized (separated by white spaces) and
         * treated according to the first token:  While commands invoke
         * corresponding Sampler member functions (see below); all other lines
         * are parsed as sampling calls by \ref add_call.  At the end of
         * `stdin` \ref go is invoked implicitly.
         *
         * | command        | arguments              | member function   |
         * | -------------- | ---------------------- | ----------------- |
         * | `set_counters` | `[` *counter* `[...]]` | \ref set_counters |
         * | `{omp`         |                        | \ref omp_start    |
         * | `}`            |                        | \ref omp_end      |
         * | `*malloc`      | *name size*            | \ref named_malloc |
         * | `*offset`      | *name offset new_name* | \ref named_offset |
         * | `free`         | *name*                 | \ref named_free   |
         * | `go`           |                        | \ref go           |
         * | `info`         | *kernel_name*          | \ref info         |
         * | `print`        | *text*                 | \ref print        |
         */
        void start();
};

#endif /* SAMPLER_HPP */

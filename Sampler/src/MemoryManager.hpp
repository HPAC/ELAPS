#ifndef MEMORYMANAGER_HPP
#define MEMORYMANAGER_HPP

#include <vector>
#include <map>
#include <string>


/** Memory manager.
 * This class manages the memory for the kernel calls' pointer arguments.
 *
 * There are three types of memory:
 * - *Static Memory*: buffers with with fixed values.  Static Memory is handled
 *   by the following member functions:
 *   | member function      | purpose                                          |
 *   | -------------------- | ------------------------------------------------ |
 *   | \ref static_register | Register and set a Static Memory buffer.         |
 *   | \ref static_get      | Get a pointer to a Static Memory variable by id. |
 *   | \ref static_reset    | Reset the Static Memory Buffer.                  |
 *
 * - *Named Memory*: named allocated buffers and offsets into such.  Named
 *   Memory is handled by the following member functions:
 *   | member function   | purpose                                              |
 *   | ----------------- | ---------------------------------------------------- |
 *   | \ref named_exists | Check if a string identifies a Named Memory buffer.  |
 *   | \ref named_malloc | Create a Named Memory buffer.                        |
 *   | \ref named_offset | Name an offset into an existing Named Memory buffer. |
 *   | \ref named_get    | Get a pointer to a Named Memory buffer.              |
 *   | \ref named_free   | Free a Named Memory buffer                           |
 *
 * - *Dynamic Memory*: dynamically assigned memory buffers
 *   Memory is handled by the following member functions:
 *   | member function       | purpose                                         |
 *   | --------------------- | ----------------------------------------------- |
 *   | \ref dynamic_newcall  | Signal that the last call completed.            |
 *   | \ref dynamic_register | Get a pointer to a Dynamic Memory buffer.       |
 *   | \ref dynamic_get      | Get a pointer to a Dynamic Memory buffer.       |
 *   | \ref dynamic_reset    | Reset the total Dynamic Buffer size to 0 bytes. |
 */
class MemoryManager {
    private:
        /** Alignment for static, malloced named, and  dynamic variables in bytes. */
        const std::size_t alignment;

        /** Offset for the first dynamic memory location for each call in bytes. */
        const std::size_t dynamic_first_offset;

        /** Static Memory buffer. */
        std::vector<char> static_mem;

        /** Malloced Named Memory buffers. */
        std::map<const std::string, char *> named_mem;

        /** Lookup for Named Memory buffers.
         * Contains both malloced bufers and named offsets.
        */
        std::map<const std::string, char *> named_map;

        /** Named Memory offset hierarchy
         * Mapping of named buffers and named offsets to relatively computed
         * offsets.  The structure is needed to free computed offsets in @ref
         * named_free.
        */
        std::map<const std::string, std::vector<std::string> > named_aliases;

        /** Dynamic Memory buffer. */
        std::vector<char> dynamic_mem;

        /** Amount of Dynamic Memory already occupied by the current call.
         * This is needed to ensure there is no aliasing between Dynamic Memory
         * buffers within a kernel call.
         */
        std::size_t dynamic_needed_curr;

        /** Randomize a buffer.
         * Fill a buffer with random elements of a data type \p T.  Uses
         * `std::rand`.
         *
         * \tparam T    Data type for which to generate random numbers.
         * \param data  Buffer of type \p T.
         * \param size  Number of elements of type \p T to randomize.
        */
        template <typename T> void randomize(void *data, std::size_t size);

        /** Prohibit default copy constructor */
        MemoryManager(const MemoryManager &that);

        /** Prohibit default copy assignment operator*/
        MemoryManager &operator=(const MemoryManager &that);

    public:
        /** Default initializer.
         *
         * \param alignment Initial value for @ref alignment.
         * \param first_offset  Initial value for @ref dynamic_first_offset.
         */
        MemoryManager(std::size_t alignment = 64, std::size_t first_offset = 0);

        /** Default destructor. */
        ~MemoryManager();

        /** Register and set a Static Memory buffer.
         * Reserve space in the Static Memory buffer for a variable of size \p
         * size, copy the value from \p value to it, and return an id for the
         * buffer.
         *
         * \param value Buffer of size \p size
         * \param size  Size of the buffer in bytes
         * \return An id to reference the reserved buffer.
         */
        std::size_t static_register(const void *value, std::size_t size);

        /** Get a pointer to a Static Memory variable by id.
         * Return a pointer to the current location of variable \p id in the
         * Static Memory buffer.
         *
         * \param id    Variable id returned by \ref static_register.
         */
        void *static_get(std::size_t id);

        /** Reset the Static Memory Buffer.
         * Deletes all registered variables and truncates the buffer to 0
         * bytes.
         */
        void static_reset();

        /** Check if a string identifies a Named Memory buffer.
         *
         * \param name  Buffer name to check for existence.
         * \return `true` such a buffer exists, else `false`.
         */
        bool named_exists(const std::string &name) const;

        /** Create a Named Memory buffer.
         * Allocates a new buffer named \p name of size \p size bytes.
         * There is no check if the name was previously already used
         *
         * \param name  Name of the buffer.
         * \param size  Size of the buffer.
         *
         */
        template <typename T> void named_malloc(const std::string &name, std::size_t size);

        /** Name an offset into an existing Named Memory buffer.
         * A buffer named \p newname is created from \p oldname by adding an
         * offset of \p size bytes.
         * There are no checks for existence.
         *
         * \param oldname   Buffer into which to set the offset.
         * \param offset    Offset in bytes.
         * \param newname   Name of the new buffer (i.e., pointer).
         */
        template <typename T> void named_offset(const std::string &oldname, std::size_t offset, const std::string &newname);

        /** Get a pointer to a Named Memory buffer.
         *
         * \param name  Name of the buffer.
         */
        void *named_get(const std::string &name);

        /** Free a Named Memory buffer.
         * Frees a Named Memory buffer and all offsets computed from it.
         *
         * \param name  Name of the buffer.
         */
        void named_free(const std::string &name);

        /** Signal that the last call completed.
         * The next requested Dynamic Memory buffer belongs to a different call
         * than the last.
         */
        void dynamic_newcall();

        /** Register a Dynamic Memory buffer.
         * Reserve a buffer for the current call of \p size elements of type \p
         * T and return an id identifying it.
         *
         * \tparam T    Requested data type.
         * \param size  Size of the buffer in terms of \p T.
         * \return An id identifying the buffer location.
         */
        template <typename T> std::size_t dynamic_register(std::size_t size);

        /** Get a pointer to a Dynamic Memory buffer.
         *
         * \param id  Id of the buffer as returned by \ref dynamic_register.
         */
        void *dynamic_get(std::size_t id);

        /** Reset the total Dynamic Buffer size to 0 bytes. */
        void dynamic_reset();
};

#endif /* MEMORYMANAGER_HPP */

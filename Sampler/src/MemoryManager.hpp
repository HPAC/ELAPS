#ifndef MEMORYMANAGER_HPP
#define MEMORYMANAGER_HPP

#include <vector>
#include <map>
#include <string>

class MemoryManager {
    private:
        // configuration parameters
        const std::size_t alignment;
        const std::size_t dynamic_first_offset;

        // static memory for arguments with fixed values (flag, size, ld, ...)
        std::vector<char> static_mem;

        // named memory
        std::map<const std::string, char *> named_mem;
        std::map<const std::string, char *> named_map;
        std::map<const std::string, std::vector<std::string> > named_aliases;

        // dynamic memory for unnamed data arguments
        std::vector<char> dynamic_mem;
        std::size_t dynamic_needed_curr; // needed to pass unaliased pointers

        // routines
        template <typename T> void randomize(void *data, std::size_t size);

        // prohibit default routines (we don't keep track of allocated memory sizes)
        MemoryManager(const MemoryManager &that);
        MemoryManager &operator=(const MemoryManager &that);

    public:
        MemoryManager(std::size_t alignment = 64, std::size_t first_offset = 0);
        ~MemoryManager();

        // static memory
        std::size_t static_register(const void *value, std::size_t size);
        void *static_get(std::size_t id);
        void static_reset();

        // named memory
        bool named_exists(const std::string &name) const;
        template <typename T> void named_malloc(const std::string &name, std::size_t size);
        template <typename T> void named_offset(const std::string &oldname, std::size_t offset, const std::string &newname);
        void *named_get(const std::string &name);
        void named_free(const std::string &name);

        // dynamic memory
        void dynamic_newcall();
        template <typename T> std::size_t dynamic_register(std::size_t size);
        void *dynamic_get(std::size_t id);
        void dynamic_reset();
};

#endif /* MEMORYMANAGER_HPP */

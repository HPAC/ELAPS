#ifndef MEMORYMANAGER_HPP
#define MEMORYMANAGER_HPP

#include <cstddef>
#include <vector>
#include <map>
#include <string>

class MemoryManager {
    private:
        // variables
        
        // configuration parameters
        const std::size_t alignment;
        const std::size_t dynamic_first_offset;

        // static memory for arguments with fixed values (flag, size, ld, ...)
        std::vector<char> static_mem;

        // named memory
        std::map<std::string, char *> named_mem;
        std::map<std::string, char *> named_map;
        std::map<std::string, std::vector<std::string> > named_aliases;

        // dynamic memory for unnamed data arguments
        std::vector<char> dynamic_mem;
        std::size_t dynamic_needed_curr; // needed to pass unaliased pointers

        // routines
        void named_delete_aliases(std::string name);

    public:
        MemoryManager(std::size_t alignment = 64, std::size_t first_offset = 0);
        ~MemoryManager();

        // static memory
        std::size_t static_register(const void *value, const size_t size);
        void *static_get(std::size_t id);
        void static_reset();

        // named memory
        bool named_exists(std::string name);
        void named_malloc(std::string name, std::size_t size);
        void named_offset(std::string oldname, std::size_t offset, std::string newname);
        void *named_get(std::string name);
        void named_free(std::string name);

        // dynamic memory
        void dynamic_newcall();
        std::size_t dynamic_register(std::size_t size);
        void *dynamic_get(std::size_t id);
        void dynamic_reset();
};

#endif /* MEMORYMANAGER_HPP */

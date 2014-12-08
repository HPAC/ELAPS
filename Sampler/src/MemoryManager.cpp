#include "MemoryManager.hpp"

#include <iostream>

#include <string.h>
#include <stdint.h>

using namespace std;

MemoryManager::MemoryManager(size_t alignment, size_t first_offset)
: alignment(alignment), dynamic_first_offset(first_offset),
  dynamic_mem(first_offset)
{ }

MemoryManager::~MemoryManager() {
    // delete named memory
    while (named_mem.size())
        named_free(named_mem.begin()->first);
}

////////////////////////////////////////////////////////////////////////////////
// static                                                                     //
////////////////////////////////////////////////////////////////////////////////

size_t MemoryManager::static_register(const void *value, const size_t size) {
    size_t length = static_mem.size();
    size_t newlength = length + (size / 8 + (size % 8 != 0)) * 8; // alignment of 8 bytes
    static_mem.resize(newlength);
    memcpy(&static_mem[length], value, size);
    return length;
}

void *MemoryManager::static_get(size_t id) {
    return &static_mem[id];
}

void MemoryManager::static_reset() {
    static_mem.resize(0);
}

////////////////////////////////////////////////////////////////////////////////
// named                                                                      //
////////////////////////////////////////////////////////////////////////////////

bool MemoryManager::named_exists(string name) {
    return (named_map.find(name) != named_map.end());
}


void MemoryManager::named_malloc(string name, size_t size) {
    if (named_map.find(name) != named_map.end()) {
        cerr << "duplicate named variable allocation:" << name << endl;
        return;
    }
    // allocate memory
    named_mem[name] = new char[size + alignment];
    // create map
    named_map[name] = (char *) (((size_t) named_mem[name] / alignment + 1) * alignment);
    named_aliases[name] = vector<string>();
}

void MemoryManager::named_offset(string oldname, size_t offset, string newname) {
    // create map
    named_map[newname] = named_map[oldname] + offset;
    // register alias
    named_aliases[oldname].push_back(newname);
}

void *MemoryManager::named_get(string name) {
    return (void *) named_map[name];
}

void MemoryManager::named_free(string name) {
    // delete all aliases
    while (named_aliases[name].size())
        named_free(named_aliases.begin()->first);
    named_aliases.erase(name);
    // delete map
    named_map.erase(name);
    // if it is not an alias itself, delete
    if (named_mem.count(name)) {
        delete[] named_mem[name];
        named_mem.erase(name);
    }
}

////////////////////////////////////////////////////////////////////////////////
// dynamic                                                                    //
////////////////////////////////////////////////////////////////////////////////

void MemoryManager::dynamic_newcall() {
    dynamic_needed_curr = dynamic_first_offset;
}

size_t MemoryManager::dynamic_register(size_t size) {
    // go to next alignment step
    size_t id = (((size_t) dynamic_needed_curr / alignment + 1) * alignment);
    // compute new end of needed
    dynamic_needed_curr = id + size;
    // if needed, extend the size of dynamic memory
    if (dynamic_needed_curr + alignment > dynamic_mem.size())
        dynamic_mem.resize(dynamic_needed_curr + alignment);
    return id;
}

void *MemoryManager::dynamic_get(size_t id) {
    return (void *) &dynamic_mem[id];
}

void MemoryManager::dynamic_reset() {
    dynamic_mem.resize(0);
}

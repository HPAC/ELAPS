#include "MemoryManager.hpp"

#include <iostream>
#include <climits>
#include <cstring>
#include <cstdlib>
#include <ctime>

using namespace std;

MemoryManager::MemoryManager(size_t alignment, size_t first_offset)
: alignment(alignment), dynamic_first_offset(first_offset),
  dynamic_mem(first_offset)
{ 
    // initialize random number generator
    srand(time(NULL));
}

MemoryManager::~MemoryManager() {
    // delete named variables
    while (named_mem.size())
        named_free(named_mem.begin()->first);
}

////////////////////////////////////////////////////////////////////////////////
// randomize memory region                                                    //
////////////////////////////////////////////////////////////////////////////////

template <> void MemoryManager::randomize<char>(void *data, size_t size) {
    // random characters (between 0 and UCHAR_MAX)
    for (size_t i = 0; i < size; i++)
        ((unsigned char *) data)[i] = rand() % UCHAR_MAX;
}

template <> void MemoryManager::randomize<int>(void *data, size_t size) {
    // random positive integers not exceeding INT_MAX (which is likely <= RAND_MAX)
    for (size_t i = 0; i < size; i++)
        ((unsigned int *) data)[i] = rand() % INT_MAX;
}

template <> void MemoryManager::randomize<float>(void *data, size_t size) {
    // random single precision number in [0, 1)
    for (size_t i = 0; i < size; i++)
        ((float *) data)[i] = ((float) rand()) / RAND_MAX;
}

template <> void MemoryManager::randomize<double>(void *data, size_t size) {
    // random double precision number in [0, 1)
    for (size_t i = 0; i < size; i++)
        ((double *) data)[i] = ((double) rand()) / RAND_MAX;
}

////////////////////////////////////////////////////////////////////////////////
// static                                                                     //
////////////////////////////////////////////////////////////////////////////////

size_t MemoryManager::static_register(const void *value, size_t size) {
    // record the start for this chunk
    const size_t oldlength = static_mem.size();

    // compute the new total size
    const size_t newlength = oldlength + (size / 8 + (size % 8 != 0)) * 8; // alignment of 8 bytes

    // increase size as needed
    static_mem.resize(newlength);

    // copy value(s) over
    memcpy(&static_mem[oldlength], value, size);

    // return the start of the chunk as its id
    return oldlength;
}

void *MemoryManager::static_get(size_t id) {
    return &static_mem[id];
}

void MemoryManager::static_reset() {
    static_mem.clear();
}

////////////////////////////////////////////////////////////////////////////////
// named                                                                      //
////////////////////////////////////////////////////////////////////////////////

bool MemoryManager::named_exists(const string &name) const {
    return (bool) named_map.count(name);
}

template <typename T>
void MemoryManager::named_malloc(const string &name, size_t size) {
    // assumption: variable doesn't exist yet (check beforehand)
    
    // allocate memory
    named_mem[name] = new char[sizeof(T) * size + alignment];

    // aligned memory registerd in the mapping
    named_map[name] = (char *) (((size_t) named_mem[name] / alignment + 1) * alignment);

    // initialially empty list of aliases
    named_aliases[name] = vector<string>();

    // put random data of correspoindng type
    randomize<T>(named_mem[name], size);
}
template void MemoryManager::named_malloc<char>(const string &name, size_t size);
template void MemoryManager::named_malloc<int>(const string &name, size_t size);
template void MemoryManager::named_malloc<float>(const string &name, size_t size);
template void MemoryManager::named_malloc<double>(const string &name, size_t size);

template <typename T>
void MemoryManager::named_offset(const string &oldname, size_t offset, const string &newname) {
    // create mapping from offset
    named_map[newname] = named_map[oldname] + offset * sizeof(T);

    // register alias
    named_aliases[oldname].push_back(newname);
}
template void MemoryManager::named_offset<char>(const string &oldname, size_t offset, const string &newname);
template void MemoryManager::named_offset<int>(const string &oldname, size_t offset, const string &newname);
template void MemoryManager::named_offset<float>(const string &oldname, size_t offset, const string &newname);
template void MemoryManager::named_offset<double>(const string &oldname, size_t offset, const string &newname);

void *MemoryManager::named_get(const string &name) {
    return (void *) named_map[name];
}

void MemoryManager::named_free(const string &name) {
    // delete all aliases
    while (named_aliases[name].size())
        named_free(named_aliases.begin()->first);
    named_aliases.erase(name);

    // delete mapping
    named_map.erase(name);

    // if it's a malloc variable, free it
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

template <typename T>
size_t MemoryManager::dynamic_register(size_t size) {
    // go to next alignment step
    const size_t id = (((size_t) dynamic_needed_curr / alignment + 1) * alignment);

    // compute new size of needed memory
    dynamic_needed_curr = id + size * sizeof(T);

    // check if resize is required
    const size_t oldsize = dynamic_mem.size();
    const size_t newsize = dynamic_needed_curr + alignment;
    if (newsize > oldsize) {

        // extend size
        dynamic_mem.resize(newsize);

        // randomize with currently requested type
        randomize<T>(&dynamic_mem[oldsize], (newsize - oldsize) / sizeof(T));
    }
    return id;
}
template size_t MemoryManager::dynamic_register<char>(size_t size);
template size_t MemoryManager::dynamic_register<int>(size_t size);
template size_t MemoryManager::dynamic_register<float>(size_t size);
template size_t MemoryManager::dynamic_register<double>(size_t size);

// void treated as char for size
template <> size_t MemoryManager::dynamic_register<void>(size_t size) {
    dynamic_register<char>(size);
}

void *MemoryManager::dynamic_get(size_t id) {
    return (void *) &dynamic_mem[id];
}

void MemoryManager::dynamic_reset() {
    dynamic_mem.resize(0);
}

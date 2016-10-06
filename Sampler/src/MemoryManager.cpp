#include "MemoryManager.hpp"

#include <iostream>
#include <climits>
#include <cstring>
#include <cstdlib>
#include <ctime>
#include <complex>

using namespace std;

MemoryManager::MemoryManager(size_t alignment_, size_t first_offset_)
: alignment(alignment_), dynamic_first_offset(first_offset_),
    dynamic_needed_total(first_offset_), dynamic_size(0), dynamic_mem(0)
{
    // initialize random number generator
    srand(static_cast<unsigned int>(time(NULL)));
}

MemoryManager::~MemoryManager() {
    // delete named variables
    while (named_mem.size())
        named_free(named_mem.begin()->first);

    // delete dynamic memory
    if (dynamic_mem)
        delete dynamic_mem;
}

/** Explicit \ref randomize instantiation for `char`.
 * Random values taken from \f$\{0, 1, \ldots, {\tt UCHAR\_MAX} - 1\}\f$.
 */
template <> void MemoryManager::randomize<char>(void *data, size_t size) {
    for (size_t i = 0; i < size; i++)
        static_cast<unsigned char *>(data)[i] = rand() % UCHAR_MAX;
}

/** Explicit \ref randomize instantiation for `int`.
 * Random values taken from \f$\{0, 1, \ldots, \min({\tt RAND\_MAX}, {\tt
 * INT\_MAX}) - 1\}\f$.
 */
template <> void MemoryManager::randomize<int>(void *data, size_t size) {
    for (size_t i = 0; i < size; i++)
        static_cast<unsigned int *>(data)[i] = rand() % INT_MAX;
}

/** Explicit \ref randomize instantiation for `float`.
 * Random values taken from \f$[0, 1)\f$.
 */
template <> void MemoryManager::randomize<float>(void *data, size_t size) {
    for (size_t i = 0; i < size; i++)
        static_cast<float *>(data)[i] = rand() / static_cast<float>(RAND_MAX);
}

/** Explicit \ref randomize instantiation for `double`.
 * Random values taken from \f$[0, 1)\f$.
 */
template <> void MemoryManager::randomize<double>(void *data, size_t size) {
    for (size_t i = 0; i < size; i++)
        static_cast<double *>(data)[i] = rand() / static_cast<double>(RAND_MAX);
}

/** Explicit \ref randomize instantiation for `complex<float>`.
 * Random values taken from \f$[0, 1) + [0, 1) i\f$.
 */
template <> void MemoryManager::randomize<complex<float> >(void *data, size_t size) {
    randomize<float>(data, 2 * size);
}

/** Explicit \ref randomize instantiation for `complex<double>`.
 * Random values taken from \f$[0, 1) + [0, 1) i\f$.
 */
template <> void MemoryManager::randomize<complex<double> >(void *data, size_t size) {
    randomize<double>(data, 2 * size);
}

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

bool MemoryManager::named_exists(const string &name) const {
    return static_cast<bool>(named_map.count(name));
}

template <typename T>
void MemoryManager::named_malloc(const string &name, size_t size) {
    // assumption: variable doesn't exist yet (check beforehand)

    // allocate memory
    named_mem[name] = new char[sizeof(T) * size + alignment];

    // aligned memory registered in the mapping
    named_map[name] = reinterpret_cast<char *>((reinterpret_cast<size_t>(named_mem[name]) / alignment + 1) * alignment);

    // initially empty list of aliases
    named_aliases[name] = vector<string>();

    // put random data of corresponding type
    randomize<T>(named_map[name], size);
}

/** \ref named_malloc instantiation for `char`. */
template void MemoryManager::named_malloc<char>(const string &name, size_t size);

/** \ref named_malloc instantiation for `int`. */
template void MemoryManager::named_malloc<int>(const string &name, size_t size);

/** \ref named_malloc instantiation for `float`. */
template void MemoryManager::named_malloc<float>(const string &name, size_t size);

/** \ref named_malloc instantiation for `double`. */
template void MemoryManager::named_malloc<double>(const string &name, size_t size);

/** \ref named_malloc instantiation for `complex<float>`. */
template void MemoryManager::named_malloc<complex<float> >(const string &name, size_t size);

/** \ref named_malloc instantiation for `complex<double>`. */
template void MemoryManager::named_malloc<complex<double> >(const string &name, size_t size);

template <typename T>
void MemoryManager::named_offset(const string &oldname, size_t offset, const string &newname) {
    // create mapping from offset
    named_map[newname] = named_map[oldname] + offset * sizeof(T);

    // register alias
    named_aliases[oldname].push_back(newname);
}

/** \ref named_offset instantiation for `char`. */
template void MemoryManager::named_offset<char>(const string &oldname, size_t offset, const string &newname);

/** \ref named_offset instantiation for `int`. */
template void MemoryManager::named_offset<int>(const string &oldname, size_t offset, const string &newname);

/** \ref named_offset instantiation for `float`. */
template void MemoryManager::named_offset<float>(const string &oldname, size_t offset, const string &newname);

/** \ref named_offset instantiation for `double`. */
template void MemoryManager::named_offset<double>(const string &oldname, size_t offset, const string &newname);

/** \ref named_offset instantiation for `complex<float>`. */
template void MemoryManager::named_offset<complex<float> >(const string &oldname, size_t offset, const string &newname);

/** \ref named_offset instantiation for `complex<double>`. */
template void MemoryManager::named_offset<complex<double> >(const string &oldname, size_t offset, const string &newname);

void *MemoryManager::named_get(const string &name) {
    return static_cast<void *>(named_map[name]);
}

void MemoryManager::named_free(const string &name) {
    // delete all aliases
    vector<string> &aliases = named_aliases[name];
    while (aliases.size()) {
        named_free(aliases.back());
        aliases.pop_back();
    }
    named_aliases.erase(name);

    // delete mapping
    named_map.erase(name);

    // if it's a malloc variable, free it
    if (named_mem.count(name)) {
        delete[] named_mem[name];
        named_mem.erase(name);
    }
}

void MemoryManager::dynamic_newcall() {
    dynamic_needed_curr = dynamic_first_offset;
}

template <typename T>
size_t MemoryManager::dynamic_register(size_t size) {
    // go to next alignment step
    const size_t id = (dynamic_needed_curr / alignment + 1) * alignment;

    // compute new size of needed memory
    dynamic_needed_curr = id + size * sizeof(T);

    if (dynamic_needed_curr > dynamic_needed_total)
        dynamic_needed_total = dynamic_needed_curr;

    return id;
}

/** \ref dynamic_register instantiation for `char`. */
template size_t MemoryManager::dynamic_register<char>(size_t size);

/** \ref dynamic_register instantiation for `int`. */
template size_t MemoryManager::dynamic_register<int>(size_t size);

/** \ref dynamic_register instantiation for `float`. */
template size_t MemoryManager::dynamic_register<float>(size_t size);

/** \ref dynamic_register instantiation for `double`. */
template size_t MemoryManager::dynamic_register<double>(size_t size);

/** Explicit \ref dynamic_register instantiation for `void`.
 * Treated as `char` in terms of size.
 */
template <> size_t MemoryManager::dynamic_register<void>(size_t size) {
    return dynamic_register<char>(size);
}

#include <stdio.h>

void *MemoryManager::dynamic_get(size_t id) {
    // need to allocate (more) dynamic memory?
    if (dynamic_size < dynamic_needed_total) {

        // free old memory
        if (dynamic_mem)
            delete dynamic_mem;

        // set new size
        dynamic_size = dynamic_needed_total;

        // allocate new memory 
        dynamic_mem = new char[dynamic_size];

        // randomize new memory
        randomize<int>(dynamic_mem, dynamic_size / sizeof(int));
    }

    return static_cast<void *>(dynamic_mem + id);
}

void MemoryManager::dynamic_reset() {
    delete dynamic_mem;
}

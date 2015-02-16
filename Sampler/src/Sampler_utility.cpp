#include "Sampler.hpp"

#include <iostream>
#include <sstream>
#include <iterator>
#include <ctime>

using namespace std;

void Sampler::print(const vector<string> &tokens) {
    ostringstream text;
    copy(tokens.begin() + 1, tokens.end(), ostream_iterator<string>(text, " "));
    cout << text.str() << endl;
}

void Sampler::date(const vector<string> &tokens) {
    cout << time(NULL) << endl;
}

void Sampler::info(const vector<string> &tokens) {
    // require 1 argument: kernel name
    if (tokens.size() < 2) {
        cerr << "No argument for " << tokens[0] << " (command ignored)" << endl;
        cerr << "usage (exmaple): " << tokens[0] << " dgemm" << endl;
        return;
    }
    if (tokens.size() > 2) {
        cerr << "Ignoring excess arguments for " << tokens[0] << endl; 
        cerr << "usage (example): " << tokens[0] << " dgemm" << endl;
    }

    const string &routine = tokens[1];

    // catch unknown routines
    if (signatures.find(routine) == signatures.end()) {
        cerr << "Uknown kernel: " << routine << " (command ignored)" << endl;
        return;
    }

    // print <routine name>(
    cerr << routine << "(";

    // print the signatue for the routine
    const Signature &signature = signatures[routine];
    const size_t argc = signature.arguments.size();
    for (unsigned char i = 1; i < argc; i++) {
        switch (signature.arguments[i]) {
            case CHARP:
                cerr << "char *";
                break;
            case INTP:
                cerr << "int *";
                break;
            case FLOATP:
                cerr << "float *";
                break;
            case DOUBLEP:
                cerr << "double *";
                break;
            case VOIDP:
                cerr << "void *";
                break;
            default:
                break;
        }
        if (i + 1 < argc)
            cerr << ", ";
    }

    // print );
    cerr << ");" << endl;
}

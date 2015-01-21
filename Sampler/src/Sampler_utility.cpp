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

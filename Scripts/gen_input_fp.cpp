// (C) 2017 University of Bristol. See License.txt

#include <iostream>
#include <fstream>
#include "Math/gfp.h"

using namespace std;

int main(int argc, char **argv) {
	istream* in;
	ostream* out;
	bool use_std=true;
	if(argc == 3) {
		use_std=false;
		in = new ifstream(argv[1]);
		out = new ofstream(argv[2], ofstream::out | ofstream::app);
	} else {
		in = &cin;
		out = &cout;
	}

	gfp::init_field(bigint("172035116406933162231178957667602464769"));

	int n; *in >> n;
	for (int i = 0; i < n; ++i) {
		bigint a;
		*in >> a;
		gfp b;
		to_gfp(b, a);
		b.output(*out, false);
	}
	if(!use_std) {
		((ifstream*)in)->close();
		((ofstream*)out)->close();
		delete in;
		delete out;
	}

	return 0;
}

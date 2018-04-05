// (C) 2018 University of Bristol. See License.txt

#include <iostream>
#include <fstream>
#include "Math/gf2n.h"
#include "Processor/Buffer.h"

using namespace std;

int main(int argc, char **argv) {
	istream* in;
	ostream* out;
	bool use_stdin = false;
	bool use_stdout = false;
	if(argc == 0) {
		in = new ifstream("gfp_vals.in");
		out = new ofstream("gfp_vals.out");
	} else if(argc == 3) {
		// Input Stream
		if (strcmp(argv[1], "-")==0){
			use_stdin = true;
			in = &cin;
		} else {
			in = new ifstream(argv[1]);
		}
		// Output Stream
		if (strcmp(argv[2], "-")==0){
			use_stdout = true;
			out = &cout;
		} else {
			out = new ofstream(argv[2]);
		}
	} else {
		cerr << "Usage: gen_input_f2n.x [<INFILE> <OUTFILE>]\n\tUse \"-\" for standard input and standard output.\n\tIf no files are specified \"gfp_vals.in\" and \"gfp_vals.out\" are used by default.";
		return 1;
	}

	gf2n::init_field(40);

	int n; cin >> n;
	for (int i = 0; i < n; ++i) {
		gf2n_short x; cin >> x;
		cerr << "value is: " << x << "\n";
		x.output(cout,false);
	}
	n = -(n % BUFFER_SIZE) + BUFFER_SIZE;
	cerr << "Adding " << n << " zeros to match buffer size" << endl;
	for (int i = 0; i < n; i++)
		gf2n(0).output(cout, false);

	// Clean up file streams.
	if(!use_stdin) {
		((ifstream*)in)->close();
		delete in;
	}
	if(!use_stdout) {
		((ofstream*)out)->close();
		delete out;
	}

	return 0;
}

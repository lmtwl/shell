#!/usr/bin/perl -w
use strict;
$|++;

use Socket qw(inet_aton inet_ntoa);

my $filename = $ARGV[0];

sub cidr2bits {
  my $cidr = shift;
  my ($addr, $maskbits) = $cidr =~ /^([\d.]+)\/(\d+)$/
    or die "bad format for cidr: $cidr";
 
  substr(unpack("B*", inet_aton($addr)), 0, $maskbits);
}

sub bits2cidr {
  my $bits = shift;
 
  inet_ntoa(pack "B*",
            substr("${bits}00000000000000000000000000000000", 0, 32))
    . "/" . length($bits);
}

sub mergecidr {
  local $_ = join "", sort map { cidr2bits($_)."\n" } @_;
  1 while s/^(\d+)0\n\1[1]\n/$1\n/m or s/^(\d+)\n\1\d+\n/$1\n/m;
  map bits2cidr($_), split /\n/;
}

open my $handle,'<',$filename;
chomp(my @lines = <$handle>);
close $handle;

if (1) {

  print join "----\n", map
    join("",
#        "from:\n", map("  $_\n", @$_),
#        "to:\n", map("  $_\n", mergecidr(@$_))),
         "to:\n", map("$_\n", mergecidr(@$_))),
           \@lines;
#          \@first, \@second, \@third;

}

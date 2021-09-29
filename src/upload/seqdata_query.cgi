#!/usr/bin/perl -T
$ENV{'PATH'} = '/usr/local/bin:/bin:/usr/local/postgresql/bin';
delete @ENV{qw(IFS CDPATH ENV BASH_ENV)};   # Make %ENV safer

######################################################################
# written by: Belinda Giardine         
######################################################################
# Requirements for this program:
# MySql
# Apache
# Perl 
# Perl Modules (DBI)
# sendmail
######################################################################
# NEED:

use DBI;
#use DBI::Profile;
use CGI qw(-debug -oldstyle_urls -no_xhtml :html4);
use CGI::Carp qw(fatalsToBrowser set_message);
use URI::Escape;
BEGIN {
  sub handle_errors {
     my $msg = shift;
     print "<h1>Found an error</h1>";
#print error to STDERR after done debugging
print $msg, "\n";
     print "The error message was sent and will be looked into.<BR>";
     send_mail("Found a bug! \nError: $msg");
  }
  set_message(\&handle_errors);
}
use strict;
use warnings;

#global variables
my $q = new CGI;
#check for errors, this should catch overflow of query string
my $error = $q->cgi_error;
if ($error) {
   print_error($error . '<br />');
}

#HARDCODED page
my $query_page = "seqdata_query.cgi";   

my $query_desc = ''; #for generated query description

#URLS FOR LINKS
#HARDCODED
my $cgi_base = "/upload/";
my $html_base = "/";
my $query_url = $cgi_base . "$query_page";
my $action = "/upload/$query_page";
#End of urls

my @bind_vars;  #variable to hold all the text to be bound in query
my $conn;       #variable to tell how to connect between boxes -- AND/OR
my $case_flag;  #flag, 1 for case matters 0 for ignore case
my $testdb = undef;
set_globals();

#HARDCODED 
my $history_days = 14; #days to keep history
my $now_log = time();  #use for timing queries

#HARDCODED
my $cookie_domain = 'seqview.psu.edu';
my $cookie_path = '/upload/';
my $dbuser = '';
my $passwd = '';

my $dbh; 
#send statement with error while testing
#$dbh->{ShowErrorStatement} = 1;
my $testing = ''; #'' or 'test_' to switch between test and real dbs
#testing changes db, history db, and cookie name
#Profiling writes to STDERR
#$dbh->{Profile} = 6;

my $history;
my $history_changed = 0;

#login to database
login_seqdata();

#decide action needed - start of program 
my $userid = $q->cookie("${testing}seqdatauserid"); 
my $newuser = 0;  #flag so know when new user
if ($q->param("userId")) {
   $userid = $q->param("userId");
}
if (!$userid && $q->remote_host() eq 'localhost') {
   #use 1 for command line tests
   $userid = 1;
}
if (!$userid) { #new user need to assign ID
   #assign using sequence from history database
   $newuser = 1; 
   #nextval for mysql
   $dbh->do("update history.userId_seq set id = LAST_INSERT_ID(id+1)");
   $userid = $dbh->selectrow_array("SELECT LAST_INSERT_ID()");
   if ($dbh && $dbh->{Active}) { $dbh->commit; }
}elsif ($userid =~ /\D/) {
   print_error("Invalid userid");
}

if ($q->param('mode')) {
   if ($q->param('mode') eq "output") {
      read_history();
      display_results($q->param("histO"));
   }elsif ($q->param('mode') eq "Submit Query") {
      my ($s, $d) = write_query();
      add_query_to_history($s, $d);
      display_history_page();
      $q->param('op', 'simpleQuery');
      log_query_time('completed');
   }elsif ($q->param('mode') eq 'Go') {
      my $op;
      read_history();
      if ($q->param('op')) {
         $op = $q->param('op');
         if ($q->param('op') eq 'display') {
            #get query and read results in parameter
            if (!$q->param("histO") or $q->param("histO") !~ /\d+/) {
               print_error("A query must be selected for the display");
            }
            display_results($q->param("histO")); 
         }elsif ($q->param('op') eq 'intersect' || $q->param('op') eq 'union'
               || $q->param('op') eq 'subtraction') {
            history_operations($q->param('op'));
            display_history_page();
         }elsif ($q->param('op') eq 'simple') {
            display_form();
         }elsif ($q->param('op') eq 'editDesc') {
            edit_description_form();
         }elsif ($q->param('op') eq 'doneDesc') {
            update_query_description($q->param("histE"), $q->param("desc1"));
	    display_history_page();
         }elsif ($q->param('op') eq 'delete') {
            my @ids = $q->param("histD");
            if (!@ids) { print_error("No queries selected for deletion"); }
            delete_history(\@ids);
            display_history_page();
         }
      }else {
         print_error("bad value for 'op' parameter");
      }
      if (!$q->param('op') && $op) { $q->param('op', $op); } #put back so logs
      log_query_time("completed"); #don't log form or history page time
   }elsif ($q->param('mode') eq 'history') {
      #request for history page
      display_history_page();
   }elsif ($q->param('mode') eq 'Jump') {
      if ($q->param("jump") eq '<id>' || $q->param("jump") =~ /\D/) {
         print_error("Need to enter an integer id to display");
      }
      display_align_detail($q->param("jump"));
   }elsif ($q->param("mode") eq 'Edit this alignment') {
      edit_align($q->param("alnpage"));
   }elsif ($q->param("mode") eq 'Edit this experiment') {
      edit_expt($q->param("exptpage"));
   }elsif ($q->param("mode") eq 'edittable') {
      edit_tab_form(); #chose table to edit
   }elsif ($q->param("mode") eq 'Edit') {
      if ($q->param("etab") eq 'seqalignment') {
         edit_align($q->param("seqalignment.id"));
      }elsif ($q->param("etab") eq 'seqexpt') {
         edit_expt($q->param("seqexpt.id"));
      }elsif ($q->param("etab") eq 'lab') {
         edit_core($q->param("lab.id"), 'lab');
      }elsif ($q->param("etab") eq 'cellline') {
         edit_core($q->param("cellline.id"), 'cellline');
      }elsif ($q->param("etab") eq 'exptcondition') {
         edit_core($q->param("exptcondition.id"), 'exptcondition');
      }elsif ($q->param("etab") eq 'expttarget') {
         edit_core($q->param("expttarget.id"), 'expttarget');
      }else {
         print_error("Unable to edit chosen table");
      }
   }elsif ($q->param("mode") eq 'Save') {
      if ($q->param("tab") eq 'seqalignment') {
         save_align($q->param("id"));
      }elsif ($q->param("tab") eq 'seqexpt') {
         save_expt($q->param("id"));
      }elsif ($q->param("tab") eq 'lab') {
         save_core('lab');
      }elsif ($q->param("tab") eq 'cellline') {
         save_core('cellline');
      }elsif ($q->param("tab") eq 'exptcondition') {
         save_core('exptcondition');
      }elsif ($q->param("tab") eq 'expttarget') {
         save_core('expttarget');
      }else {
         print_error("Unable to save entry");
      }
      #display start form
      display_form();
   }
}elsif ($q->param("exptpage")) {
   display_expt_detail($q->param("exptpage"));  
}elsif ($q->param("alnpage")) {
   display_align_detail($q->param("alnpage"));
}else {
   #just entered page display form
   display_form();
}

if ($dbh && $dbh->{Active}) { $dbh->commit; $dbh->disconnect; }
exit;

######################################################################
# SUBROUTINES general purpose and history
######################################################################

#subroutine to print error page
sub print_error {
   my($msg) = @_;
   print $q->header(-type => 'text/html', -charset=>"ISO-8859-1");
   print $q->start_html('Problems'),
   $q->h2('Request not processed'),
   $q->strong($msg),
   $q->br,
   "userid ", $userid,
   $q->br,
   $q->end_html, "\n";
   if ($dbh && $dbh->{Active}) { $dbh->rollback; $dbh->disconnect; }
   log_query_time("error($msg)"); 
   exit 0;
}
####End of print_error

sub print_error_plain_text {
   my($msg) = @_;
   print 'Request not processed', "\n",
         $msg, "\n";
   if ($dbh && $dbh->{Active}) { $dbh->rollback; $dbh->disconnect; }
   exit 0;
}
####End of subroutine print_error_plain_text

#subroutine to send an email
sub send_mail {
   my($msg) = @_;
   #HARDCODED email address
   #query page is not defined if syntax error
   my $addr = 'giardine@bx.psu.edu';
   open(MAIL, "|/usr/lib/sendmail -t") or die;
   print(MAIL "From: seqdata_query\n");
   print(MAIL "To: $addr\n");
   print(MAIL "Subject: Seqdata query page error\n");
   print(MAIL "\n");
   print(MAIL "Error on page $query_page\n");
   print(MAIL "$msg\n");
   close(MAIL) or die;
}
####End of subroutine send_mail

#this reads the history from the db into an array
sub read_history {
   $history = $dbh->selectall_hashref("SELECT queryindex, description, "
           . "dateran, resultcount, historyid FROM history.uhistory WHERE userId = ?",
           'QUERYINDEX', undef, $userid);
}
####End of subroutine read_history

#this adds the current results to history
sub add_history {
   my $desc = shift;
   my $cnt = shift;
   my $histId = shift;
   my $qIndex = $dbh->selectrow_array("SELECT max(queryindex) FROM history.uhistory " 
           . "WHERE userId = ?", undef, $userid);
   $qIndex++;

   my $sql = "INSERT INTO history.uhistory (userId, queryindex, description, dateran, "
           . "lastaccess, resultcount, historyid) VALUES (?, ?, ?, " 
           . "current_timestamp, current_timestamp, ?, ?)";
 
   $dbh->do($sql, undef, $userid, $qIndex, $desc, $cnt, $histId);
   #add history to log table
   $sql = "INSERT INTO history.log_queries (userid, description, dateran, resultCount)".
          " VALUES (?, ?, current_timestamp, ?)";
   $dbh->do($sql, undef, $userid, $desc, $cnt);
   return $qIndex;
}
####End of subroutine add_history

#this deletes entries from a history
sub delete_history {
   my $id_ref = shift @_;
   my $sql = "SELECT historyid FROM history.uhistory WHERE userid = ? AND queryindex IN (";
   my $sql2 = "DELETE FROM history.uhistory WHERE userid = ? AND queryindex IN (";
   my $sql3 = "DELETE FROM history.query_results where historyid IN (";
   my $clause = '';
   my @ids;
   foreach (@$id_ref) {
      if ($_ eq ' ') { next; } #skip blank
      $clause .= "?, ";
      push(@ids, $_);
   }
   $clause =~ s/, $/)/;
   if ($clause !~ /\?/) { print_error("No queries to be deleted"); }
   my $hId = $dbh->selectcol_arrayref($sql . $clause, undef, $userid, @ids);
   my $clause3 = '';
   foreach (@$hId) {
      $clause3 .= "?, ";
   }
   $clause3 =~ s/, $/)/;
   $dbh->do($sql2 . $clause, undef, $userid, @ids);
   if ($clause3 =~ /\?/) {
      $dbh->do($sql3 . $clause3, undef, @$hId);
   }
}
####End of subroutine delete_history

#this updates the last access time on a users history
sub update_lastAccess {
   my $sth = $dbh->prepare("update history.uhistory set lastAccess = current_timestamp where " 
             . "userId = ?");
   $sth->execute($userid);
#do cleanup in a cron script to not slow queries NEED this script
}
####End of subroutine update_last_access

#this changes a query's description
sub update_query_description {
   my $qIndex = shift @_;
   my $desc = shift @_;
   $dbh->do("update history.uhistory set description = ? where userid = ? and queryindex = ?",
      undef, $desc, $userid, $qIndex);
}
####End of subroutine update_query_description

#sort ranges by chromosome and start point
sub sort_ranges {
   my($rang) = @_;  #ref to array of strings chr:st-stp
   #use perl function to sort
   #faster expects chrX and chrY renamed with numbers
   my(@chr, @st);
   foreach (@$rang) {
      s/chrX/chr100/;
      s/chrY/chr101/;
      s/chrW/chr102/;
      s/chrZ/chr103/;
      if (/chr(\d+)\t(\d+)/) { 
         push(@chr, $1);
         push(@st, $2);
      }else {
         /chr(\d+):(\d+)-/;
         push(@chr, $1);
         push(@st, $2);
      }
   }
   @$rang = @$rang[ sort {
                           $chr[$a] <=> $chr[$b] ||
                           $st[$a]  <=> $st[$b]
                         } 0..$#{$rang}
                  ];
   foreach (@$rang) {
      s/chr100/chrX/;
      s/chr101/chrY/;
      s/chr102/chrW/;
      s/chr103/chrZ/;
   }
   #return @sorted by altering list sent in by reference
}
####End of subroutine sort_ranges

#this subroutine handles the operations from the history page
sub history_operations {
   my $op = shift @_;
   my $s; #sql
   my $d; #description
   if ($op eq 'intersect') {
      ($s, $d) = do_intersection();
   }elsif ($op eq 'union') {
      ($s, $d) = do_union();
   }elsif ($op eq 'subtraction') {
      ($s, $d) = do_subtraction();
   }else {
      $op =~ s/\W/?/g;
      print_error("Bad value for 'op' $op\n");
   }
   add_query_to_history($s, $d); #needs sql and description
}
####End of subroutine history_operations

#do an subtraction or butNot on the query results using the database
sub do_subtraction {
   my $hist1 = $q->param("histS");
   my $hist2 = $q->param("histS2");
   if (!$hist1 or !$hist2 or $hist1 =~ /^\s*$/ or $hist2 =~ /^\s*$/) {
      print_error("Two queries must be selected to do subtraction");
   }
   #no EXCEPT in mysql 
   my $s = "SELECT id FROM history.query_results " .
      "WHERE historyid = (SELECT historyid FROM history.uhistory WHERE userid = ? " .
      "AND queryindex = ?) AND id NOT IN (SELECT id FROM history.query_results " .
      "WHERE historyid = (SELECT historyid FROM history.uhistory WHERE userid = ? " .
      "AND queryindex = ?))"; 
   push(@bind_vars, $userid, $hist1, $userid, $hist2);
   my $desc = "alignments that are in query $hist1 but not in query $hist2";
   return ($s, $desc);
}
####End of subroutine do_subtraction

#do an union of 2 queries using the database
sub do_union {
   my $hist1 = $q->param("histU");
   my $hist2 = $q->param("histU2");
   if (!$hist1 or !$hist2 or $hist1 =~ /^\s*$/ or $hist2 =~ /^\s*$/) {
      print_error("Two queries must be selected to do union");
   }
   my $s = "SELECT id FROM history.query_results " .
      "WHERE historyid = (SELECT historyid FROM history.uhistory WHERE userid = ? " .
      "AND queryindex = ?) UNION SELECT id FROM history.query_results " .
      "WHERE historyid = (SELECT historyid FROM history.uhistory WHERE userid = ? " .
      "AND queryindex = ?)"; 
   push(@bind_vars, $userid, $hist1, $userid, $hist2);
   my $desc = "alignments that are in either query $hist1 or $hist2";
   return($s, $desc);
}
####End of subroutine do_union

#do an intersection by ID on 2 queries using the database
sub do_intersection {
   my $hist1 = $q->param("histI");
   my $hist2 = $q->param("histI2");
   if (!$hist1 or !$hist2 or $hist1 =~ /^\s*$/ or $hist2 =~ /^\s*$/) {
      print_error("Two queries must be selected to do intersection");
   }
   #no INTERSECT command in mysql...
   my $s = "SELECT id FROM history.query_results " .
      "WHERE historyid in (SELECT historyid FROM history.uhistory WHERE userid = ? " .
      "AND queryindex = ?) AND id in (SELECT id FROM history.query_results " .
      "WHERE historyid in (SELECT historyid FROM history.uhistory WHERE userid = ? " .
      "AND queryindex = ?))"; 
   push(@bind_vars, $userid, $hist1, $userid, $hist2);
   my $desc = "alignments that are in both queries $hist1 and $hist2";
   return($s, $desc);
}
####End of subroutine do_intersection

#this displays a page for when there is no history
sub display_empty_history {
   start_html();
   print "Either there are no queries in the history or cookies " .
         "need turned on so that this page can work.";
   if ($dbh && $dbh->{Active}) { $dbh->commit; $dbh->disconnect; }
   exit;
}
####End of subroutine display_empty_history

#subroutine to sort by number
sub bynumber { $a <=> $b; }
####End of subroutine bynumber

#subroutine to sort case incensitively
sub nocase {uc($a) cmp uc($b)}
####End of subroutine nocase

#subroutine to sort by chromosome, mixed alpha and numeric
sub sort_chrs {
   my(@old) = @_;
   my(@c);
   foreach (@old) { 
      if (/chrX/) { $_ = 'chr100'; } 
      if (/chrY/) { $_ = 'chr101'; }
      if (/chrW/) { $_ = 'chr102'; }
      if (/chrZ/) { $_ = 'chr103'; }
      push(@c, /chr(\d+)/); 
   }
   my(@new) = @old[sort {$c[$a] <=> $c[$b]} 0..$#old];
   foreach (@new) { 
      if (/chr100/) { $_ = 'chrX'; }
      if (/chr101/) { $_ = 'chrY'; }
      if (/chr102/) { $_ = 'chrW'; }
      if (/chr103/) { $_ = 'chrZ'; }
   }
   return @new;
}
####End of subroutine sort_chrs

#this compares 2 chroms and returns 
sub lesser_chrs {
   my($chr1, $chr2) = @_;
   $chr1 =~ s/chr//;
   $chr1 =~ s/X/100/;
   $chr1 =~ s/Y/101/;
   $chr1 =~ s/W/102/;
   $chr1 =~ s/Z/103/;
   $chr2 =~ s/chr//;
   $chr2 =~ s/X/100/;
   $chr2 =~ s/Y/101/;
   $chr2 =~ s/W/102/;
   $chr2 =~ s/Z/103/;
   if ($chr1 > $chr2) { return 1; }
   return 0;
}
####End of subroutine lesser_chrs

#this adds commas to a number for readability, code from perldoc perlfaq5.pod
sub commify {
   local $_  = shift;
   1 while s/^([-+]?\d+)(\d{3})/$1,$2/;
   return $_;
}
####End of subroutine commify

#this gets a list of chroms used in a list of ranges
sub list_chroms {
   my($ranges) = @_;
   my(@chr, $lst, $s, $e, @f);
   if ($ranges->[0] =~ /\t/) {
      @f = split(/\t/, $ranges->[0]);
      $lst = $f[0];
      $s = $f[1];
      $e = $f[2];
   }else {
      ($lst, $s, $e) = split(/:|-/, $ranges->[0]);
   }
   my @t = ($lst, $s, $e);
   push(@chr, \@t);  #put first one in list
   foreach (@$ranges) {
      if (/\t/) { @f = split(/\t/); }
      else { @f = split(/:|-/); }
      if ($f[0] ne $lst) { 
         my(@t) = ($f[0], $f[1], $f[2]);  #only put chrom start stop in list
         push(@chr, \@t); 
         $lst = $f[0]; 
      }else { #adjust end
         $chr[$#chr][2] = $f[2];
      }
   }
   return @chr;
}
####End of subroutine list_chroms

#this removes undefined elements from an array
sub remove_undefs {
   my($arref) = @_;
   my($i, $j);
   $i = 0;
   while ($i <= $#{$arref} && $arref->[$i]) { $i++; }
   $j = $i;
   while ($j <= $#{$arref}) {
      $j++;
      if (!$arref->[$j]) { next; }
      $arref->[$i] = $arref->[$j];
      $i++; 
   }
   splice(@$arref, $i);
}
####End of subroutine remove_undefs

#this subroutine adds the query string to a log file for each query submitted
sub log_query {
   my @now = localtime(time);
   #zero pad the minutes
   if ($now[1] < 10) { $now[1] = "0$now[1]"; }
   print STDERR ++$now[4], "/$now[3] $now[2]:$now[1] mahonylab $query_page: ";
   my $p;
   foreach $p ($q->param) { 
      if (defined $q->param($p)) { 
         foreach ($q->param($p)) {
            if (!defined or $_ eq '' or $_ eq ' ') { next; }
            print STDERR "$p='$_'; "; 
         }
      }
   }
   #print the IP address so can exclude my testing
   print STDERR "IP='", $q->remote_host(), "'; ";
   print STDERR "USERID=$userid; ";
   print STDERR "\n";
}
####End of subroutine log_query

#this adds the length of time for the query to the logs
sub log_query_time {
   my($stage) = @_;
   my @now = localtime(time);
   #zero pad the minutes
   if ($now[1] < 10) { $now[1] = "0$now[1]"; }
   print STDERR ++$now[4], "/$now[3] $now[2]:$now[1] mahonylab $query_page: ";
   print STDERR "$stage=", time() - $now_log, 
                " IP='", $q->remote_host(), "' ",
                "USERID=$userid";
   if ($stage eq 'completed' && $q->param("op")) {
      print STDERR " op=", $q->param("op");
   }
   print STDERR "\n";
}
####End of subroutine log_query_time

#this checks the length of a list for the query description and truncates as 
#needed
sub write_desc_list {
   my($listref) = @_;
   my $list = join(", ", @{$listref});
   if (length $list > 30) {
      #chop it off
      $list = substr($list, 0, 29);
      $list .= "..";
   }
   return $list;
}
####End of subroutine write_desc_list

#this displays the form to allow the user to edit a queries description.
sub edit_description_form {
   my @hist = $q->param("histE");
   if (!@hist or $hist[0] eq ' ') { 
      print_error("You must select a query to edit it's description");
   }
   read_history();
   start_html("Edit query description");
   $q->delete("op"); #clear before print, bug in CGI.pm prints old value
   print $q->start_form;
   if (!$history->{$hist[0]}->{DESCRIPTION}) {
      $history->{$hist[0]}->{DESCRIPTION} = "[blank]";
   }
   print "Current description: ", $history->{$hist[0]}->{DESCRIPTION},
         $q->br;
   print $q->textarea(-name=>"desc1",  #may add more than one later?
                      -rows=>3,
                      -cols=>50);
   print $q->hidden("histE", @hist),
         $q->hidden("op", "doneDesc");
   print $q->br,
         $q->submit("mode", "Go");
   print $q->end_form,
         $q->end_html;
}
####End of subroutine edit_description_form

#this prints a dump of a table
sub print_table_dump {
   my($table, $sql, @binds) = @_;
   my $sth;
   my @cols;
   eval {
      $sth = $dbh->prepare($sql);
      $sth->execute(@binds);
      @cols = @{$sth->{NAME_uc}};
   };
   if ($@) {
      send_mail("There was a bug in prepare or execute in print_table_dump.\n" .
                "ERROR $@\n" .
                "SQL: $sql\n" . "BINDS: " . join(", ", @binds) . "\n");
      print_error_plain_text("Sorry there was an error.");
   }
   print "#$table: ", join("\t", @cols), "\n";
   my @row;
   my $ct = 0;
   while (@row = $sth->fetchrow_array) {
      print join("\t", @row), "\n";
      $ct++;
   }
}
####End of subroutine print_table_dump

#this prints a message (not an error) 
sub print_message {
   my($title, $msg) = @_;
   $q->delete_all(); #remove so will display all links?
   $q->param("mode", "all");
   start_html($title);
   print $msg;
   print $q->end_html, "\n";
}
####End of subroutine print_message

#this reads the results from the history tables and loads them into the query
#string
sub load_results {
   my $qIndex = shift @_;
   if (!$qIndex) { print_error("A query index is required"); }
   if ($qIndex =~ /\D/) { print_error("Invalid query index"); }
   my @hist = $dbh->selectrow_array(
      "SELECT historyid, description, to_char(dateran, 'Month dd, YYYY')" .
      " FROM history.uhistory WHERE userid = ? AND queryindex = ?", 
      undef, $userid, $qIndex);
   if (!@hist) {
      print_error("Failed to get history id for $userid and query $qIndex");
   }
   my $id = $dbh->selectcol_arrayref("SELECT id FROM history.query_results " .
      "WHERE historyid = ? ORDER BY id", undef, $hist[0]);
   $q->delete("i", "desc", "queryIndex", "dateRan"); #make sure empty
   $q->param("i", @$id) if $id;
   $q->param("desc", $hist[1]);
   $q->param("queryIndex", $qIndex);
   $q->param("dateRan", $hist[2]);
}
####End of subroutine load_results

#this adds a new query to the users history
sub add_query_to_history {
   my $sql = shift;
   my $desc = shift;
   #nextval (for mysql)
   $dbh->do("update history.historyId_seq set id = LAST_INSERT_ID(id+1)");
   my $idref = $dbh->selectrow_arrayref("select LAST_INSERT_ID()");
   my $h = $idref->[0];
   if (!$h) { print_error("Unable to extract next history ID"); }
   #change sql to include historyId
   my $sql2 = $sql;
   $sql2 =~ s/select id/select $h, id/i;
   $sql2 =~ s/UNION SELECT Id/UNION select $h, id/ig;
   $dbh->do("insert into history.query_results (historyID, id) $sql2", undef, @bind_vars);
   my $cnt = $dbh->selectrow_arrayref("select count(*) from history.query_results where historyid = ?", undef, $idref->[0]);
   my $queryInd = add_history($desc, $cnt->[0], $h);
}
####End of subroutine add_query_to_history

#this displays the history page for a user
sub display_history_page {
   read_history();
   #print header and initial html
   start_html("History page");
   print $q->start_form,
         $q->start_dl;
   print "\n";
   print_history_section();
   print "\n";
   print_actions(); #print the actions section of the form
   print "\n";
   print $q->submit(-name=>"mode", -value=>"Go"), "\n";
   print $q->br, '<div align="right">',
         $userid, '</div>';
   #close the html
   print $q->end_form;
   #NEED could clear form variables with javascript? and -onSubmit
   print $q->start_form(-name=>"clr", -action=>$query_url),
         $q->hidden('mode', 'history'),
         $q->submit(-name=>"c",
                    -value=>"Clear form"),
         $q->end_form;
   print $q->end_dl,
         $q->end_html;
}
####End of subroutine display_history_page

######################################################################
# SUBROUTINES for seqdata queries
######################################################################

#logon to seqdata database 
sub login_seqdata {
   #read in passwords etc
   my %props = read_mysqlconfig_file();
   my ($username,$passwd,$conn) = @props{qw(user passwd dbiconnectstring)};
   eval {
      $dbh = DBI->connect($conn, $username, $passwd,
           {RaiseError=>1, AutoCommit=>0});
   };
   if ($@) {
      send_mail("seqdata connect error: $@");
      print_error("Sorry the database is down for maintenance, try again " .
                   "later.");
   }
   $dbh->{ShowErrorStatement} = 1;
   $dbh->{FetchHashKeyName} = 'NAME_uc';
   if ($conn =~ /127/) { $testdb = "banba.vmhost"; }
}

sub read_mysqlconfig_file {
  my ($self) = @_;
  my $homedir = './'; #look in current directory
  my $basename = 'seqdata_passwd';
  if ($ENV{'READDBROLE'}) {
    $basename = $ENV{'READDBROLE'} . $basename;
  }
  open(PROPS,"${homedir}/.${basename}") or die "can't open config file .$basename in $homedir : $!";
  my %props = ();
  while(<PROPS>) {
    chomp;
    s/^\s*//;
    s/\s*$//;
    my ($k,$v) = ($_ =~ /([^=]*)\s*=\s*(.*)/);
    next unless ($k);
    $props{$k} = $v;
  }
  return %props;
}


#this starts the html prints title and heading
sub start_html {
   my($page, $title) = @_;
   my $cookie = $q->cookie(-name=>"${testing}seqdatauserid",
                           -value=> $userid,
                           -expires=> '+7y',
                           -domain=> $cookie_domain,
                           -path=> $cookie_path,
                           -SameSite=> 'Strict'
                           );
   my($i, $max);
   print $q->header(-type=>"text/html", -cookie=>[$cookie]);
   if (!$title) { $title = "Seqdata query page"; }
   if ($q->param("op") && $q->param("op") eq 'display' && 
       $q->param("display_format") && 
       ($q->param("display_format") eq "expts" || $q->param("display_format") eq "aligns" || $q->param("display_format") eq "exptalign")) {
      #use data tables for table displays
     my $jscode = '$(document).ready(function() {'. "\n".
               'var table = $(\'#sorttab\').DataTable({ '. "\n".
               '   order: [[ 0, "asc" ]], '. "\n".
               '   paging: false, ' . "\n" .
               '   info: false, ' . "\n" .
               '   fixedHeader: true, ' . "\n" .
               '   dom: \'Bfrtip\', ' . "\n" .
               '   buttons: [\'copy\', \'csv\', \'colvis\'], ' . "\n";
     #if ($q->param("display_format") eq "qtab") {
        #$jscode .= '   columnDefs: [ { type: \'numeric-comma\', targets: [3,4,5] } ] ' . "\n";
     #} 
     $jscode .= ' }); ' . "\n" .
               '$(window).resize( function () {' . "\n" .
               '   table.fnAdjustColumnSizing(); });' . "\n" .
               "});\n";

      print $q->start_html(-title=>$title, -bgcolor=>"WHITE",
              -meta=>{charset=>"utf8"},
              -style=>[{-src=>"/static/upload/DataTables/datatables.css", -type=>"text/css"}],
              -script=>[{-src=>"/static/upload/DataTables/datatables.js", -type=>"text/javascript", -charset=>"utf8"}, {-src=>"/static/upload/DataTables/numeric-comma.js", -type=>"text/javascript"}, {-src=>"/static/upload/DataTables/Buttons-1.2.0/js/buttons.html5.min.js", -charset=>"utf8"}, {-code=>"$jscode", -type=>"text/javascript", -language=>"javascript", -class=>"init"}])
         or die "Couldn't write start of html page, $!";
   }else {
      my $jscode = '$(document).ready(function() {' . "\n" .
                   ' $(".js-basic-multiple").select2();' . "\n" .
                   '});' . "\n";
      #for library detail page, more/less for file links
      $jscode .= 'function moreLess(prid) { ' . "\n" .
                 'var dots = document.getElementById("dots"+prid);' . "\n" .
                 'var moreText = document.getElementById("more"+prid);' . "\n" .
                 'var btnText = document.getElementById("moreLessBtn"+prid);' . "\n" .
                 'if (dots.style.display === "none") {' . "\n" .
                   'dots.style.display = "inline";' . "\n" .
                   'btnText.innerHTML = "more"; ' . "\n" .
                   'moreText.style.display = "none";' . "\n" .
                 '} else {' . "\n" .
                   'dots.style.display = "none";' . "\n" .
                   'btnText.innerHTML = "less"; ' . "\n" .
                   'moreText.style.display = "inline";' . "\n" .
                 '}' . "\n" .
                 '}';
      print $q->start_html(-title=>$title, -bgcolor=>"WHITE",
              -style=>[{-src=>"/static/upload/hbvar.css", -type=>"text/css"},{-src=>"/static/upload/select2/css/select2.min.css", -type=>"text/css"}],
              -script=>[{-src=>"/static/upload/hbvar.js", -type=>"text/javascript"}, {-src=>"https://code.jquery.com/jquery-1.10.2.min.js"}, {-src=>"/static/upload/select2/js/select2.min.js", -type=>"text/javascript"}, {-code=>"$jscode", -type=>"text/javascript", -language=>"javascript", -class=>"init"}])
         or die "Couldn't write start of html page, $!";
   }
   #print link bar across top ?
   if (!$q->param("mode") && !$q->param("op") && !$q->param("runpage") && !$q->param("libpage") && !$q->param("cellpage")) {
      #initial form
      print 'Query&nbsp;form&nbsp;',
            ' | ',
            $q->a({href=>"$query_url?mode=history", target=>"_top"},
                  'Query&nbsp;history'),
            ' | ',
            $q->a({href=>"$query_url?mode=edittable"}, 'Edit table'),
            ' | ',
            $q->start_form(-style=>"display:inline;"),
            'Jump to alignment ',
            $q->textfield(-name=>"jump", 
                        -value=>"<id>",
                        -size=>8),
            $q->submit(-name=>"mode", 
                       -value=>"Jump"),
            $q->end_form,
            $q->hr({size=>3, color=>"#FF0000"});
   }elsif ($q->param('mode') &&
           (($q->param('mode') eq 'history' ||
             $q->param('mode') eq 'Submit Query')  ||
             ($q->param('op') &&
              ($q->param('op') eq 'intersect' ||
               $q->param('op') eq 'union' ||
               $q->param('op') eq 'subtraction' ||
               $q->param('op') eq 'doneDesc' ||
               $q->param('op') eq 'delete') ))) {
      #NEED other params that generate history
      print $q->a({href=>"$query_url", target=>"_top"},
                  'Query&nbsp;form'),
            ' | ',
                  'Query&nbsp;history',
            ' | ',
            $q->a({href=>"$query_url?mode=edittable"}, 'Edit table'),
            $q->hr({size=>3, color=>"#FF0000"});
   }else { #show all links
      print $q->a({href=>"$query_url", target=>"_top"},
                  'Query&nbsp;form'),
            ' | ',
            $q->a({href=>"$query_url?mode=history", target=>"_top"},
                  'Query&nbsp;history'),
            ' | ',
            $q->a({href=>"$query_url?mode=edittable"}, 'Edit table'),
            ' | ',
            $q->start_form(-style=>"display:inline;"),
            'Jump to alignment ',
            $q->textfield(-name=>"jump",
                        -value=>"<id>",
                        -size=>8),
            $q->submit(-name=>"mode",
                       -value=>"Jump"),
            $q->end_form,
            $q->hr({size=>3, color=>"#FF0000"});
   }

   print $q->h2("Seqdata: Mahony lab database");
   if ($page) { print $q->strong($page); }
   #print $q->br;
}
####END of subroutine start_html

sub start_html_searchpanes {
   my($page, $title) = @_;
   my $cookie = $q->cookie(-name=>"${testing}seqdatauserid",
                           -value=> $userid,
                           -expires=> '+7y',
                           -domain=> $cookie_domain,
                           -path=> $cookie_path,
                           -SameSite=> 'Strict'
                           );
   my($i, $max);
   print $q->header(-type=>"text/html", -cookie=>[$cookie]);
   if (!$title) { $title = "Seqdata query page"; }

   my $coldeffalse = ''; #list of columns to not put in search panes
   if ($page && $page eq 'Experiment and alignment table') {
      $coldeffalse = '0,11,15,17,23,24,25,26,27,28,29,30,31'; 
   }elsif ($page && $page eq 'Experiment table') {
      $coldeffalse = '0,11,12,15';
   }elsif ($page && $page eq 'Alignment table') {
      $coldeffalse = '0,6,7,8,9,10,11,12,13,14,15';
   }

   #start page for datatables only
   my $jscode = '$(document).ready(function() {'. "\n".
               'var table = $(\'#sorttab\').DataTable({ '. "\n".
               '   order: [[ 0, "asc" ]], '. "\n".
               '   paging: true, ' . "\n" .
               '   info: true, ' . "\n" .
               '   searching: true, ' . "\n" .
               '   deferRender:    true, ' . "\n" .
               '   scrollY:        "500px", ' . "\n" .
               '   scrollX:        true, ' . "\n" .
               '   scrollCollapse: true, ' . "\n" .
               '   scroller:       true, ' . "\n" .
               #not working???
               #'   fixedHeader: true, ' . "\n" .
               '   dom: \'<"split left"P><"split right"Bifrtp>\', ' . "\n" .
               '   colReorder: true, ' . "\n" .
               #'   select: true, ' . "\n" .
               '   searchPanes: { cascadePanes: true, layout: \'columns-1\'  }, ' . "\n";
   if ($coldeffalse ne '') {
      $jscode .= '   columnDefs: [ { searchPanes: { show: false, }, targets: [' . $coldeffalse . '] } ],' . "\n";
   }
               #'   columnDefs: [ { searchPanes: { show: true, }, targets: [1,2,4,5,9,10,12,14,15], }, ' . "\n".
               #'                 { searchPanes: { show: false, }, targets: [0,3,6,7,8,11,13,16,17,18,19,20,21,22,23] } ],' . "\n" .
               #'   columnDefs: [ { type: \'numeric-comma\', targets: ' . $numCols . ' } ],' . "\n" .
               #lose colvis with split div
   $jscode .= '   buttons: [' .  #\'searchPanes\', ' . "\n" .
               '             { extend: \'copy\', exportOptions: { columns: \':visible\' } },' . "\n" .
               '             { extend: \'csv\', exportOptions: { columns: \':visible\' } } ' . "\n" .
               #'             \'colvis\'' . "\n" .
               '             ] ' . "\n";  #end buttons
     $jscode .= " }); \n" . #end var table
               "});\n";  #end document ready
      print $q->start_html(-title=>$title, -bgcolor=>"WHITE",
              -meta=>{charset=>"utf8"},
              -style=>[{-src=>"/static/upload/DataTables/datatables.css", -type=>"text/css"}, {-src=>"/static/upload/DataTables/Buttons-1.6.2/css/buttons.html5.min.css", -type=>"text/css"}, {-src=>"/static/upload/DataTables/SearchPanes-1.1.1/css/datatables.searchPanes.css", -type=>"text/css"}, {-src=>"/static/upload/hbvar.css", -type=>"text/css"} ],
              -script=>[{-src=>"https://code.jquery.com/jquery-1.10.2.min.js", -type=>"text/javascript"}, {-src=>"/static/upload/DataTables/datatables.js", -type=>"text/javascript", -charset=>"utf8"}, {-src=>"/static/upload/DataTables/Buttons-1.6.2/js/buttons.print.min.js", -charset=>"utf8"}, {-src=>"/static/upload/DataTables/Buttons-1.6.2/js/buttons.html5.min.js", -charset=>"utf8"}, {-code=>"$jscode", -type=>"text/javascript", -language=>"javascript", -class=>"init"}, {-src=>"/static/upload/DataTables/SearchPanes-1.1.1/js/dataTables.searchPanes.js", -type=>"text/javascript", -charset=>"utf8"}, {-src=>"/static/upload/DataTables/Responsive-2.2.5/js/dataTables.responsive.min.js", -type=>"text/javascript"}])
         or die "Couldn't write start of html page, $!";

   #print link bar across top
      print $q->a({href=>"$query_url", target=>"_top"},
                  'Query&nbsp;form'),
            ' | ',
            $q->a({href=>"$query_url?mode=history", target=>"_top"},
                  'Query&nbsp;history'),
            ' | ',
            $q->a({href=>"$query_url?mode=edittable"}, 'Edit table'),
            ' | ',
            $q->start_form(-style=>"display:inline;"),
            'Jump to alignment ',
            $q->textfield(-name=>"jump",
                        -value=>"<id>",
                        -size=>8),
            $q->submit(-name=>"mode",
                       -value=>"Jump"),
            $q->end_form,
            $q->hr({size=>3, color=>"#FF0000"});   
   print $q->h3("Seqdata: Mahony lab database");
   if ($page) { print $q->strong($page); }
}
####END of start_html_searchpanes

#this subroutine prints the actions section of the history page
sub print_actions {
   #clear previous selections
   $q->delete_all();
   print '<dt><b>Actions</b></dt>';
   print '<dd>';
   my @indexes = sort bynumber keys %{$history};
   unshift(@indexes, ' ');
   my %display;
   $display{"exptalign"} = ' Table of experiments and alignments ';
   $display{"expts"} = ' Table of experiments ';
   $display{"aligns"} = ' Table of alignments ';
   my @opt = qw(exptalign expts aligns); 
   my %label;
   my $defaultDisplay = 'exptalign';
   $label{'display'} = 'Display results for query';
   #NEED to allow more than one to expand/collapse?
   print $q->radio_group(-name=>"op", -value=>'display', 
                         -onClick=> "javascript:expand_always('disp')",
			 -default=>'display',
                         -labels=>\%label), '&nbsp;',
         $q->scrolling_list(-name=>"histO",
                            -values=>\@indexes,
                            -default=>$indexes[$#indexes],
                            -size=>1),
         '<div id="disp" style="display: block;">', #open by default
         '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;', 
         "display format ",
         $q->br, '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;',
         $q->radio_group(-name=>"display_format",
                         -value=> \@opt,
			 -default=>$defaultDisplay, 
                         -labels=> \%display),
         $q->br,
         '</div>',
         $q->br;
   
   $label{'intersect'} = 'Alignments that are in both queries';
   print $q->radio_group(-name=>'op', -value=>'intersect',
                         -onClick=> "javascript:collapse('disp')",
			 -default=>"_",
                         -labels=>\%label),
         $q->scrolling_list(-name=>"histI",
                            -values=>\@indexes,
                            -size=>1),
         ' and ',
         $q->scrolling_list(-name=>"histI2",
                            -values=>\@indexes,
                            -size=>1),
         $q->br;

   $label{'union'} = 'Alignments that are in either query';
   print $q->radio_group(-name=>'op', -value=>'union', -labels=>\%label,
			 -default=>"_",
                         -onClick=> "javascript:collapse('disp')"),
         $q->scrolling_list(-name=>"histU",
                            -values=>\@indexes,
                            -size=>1),
         ' or ',
         $q->scrolling_list(-name=>"histU2",
                            -values=>\@indexes,
                            -size=>1),
         $q->br;

   $label{'subtraction'} = 'Alignments that are in query';
   print $q->radio_group(-name=>'op', -value=>'subtraction', -labels=>\%label,
			 -default=>"_",
                         -onClick=> "javascript:collapse('disp')"),
         $q->scrolling_list(-name=>"histS",
                            -values=>\@indexes,
                            -size=>1),
         ' but not in query ',
         $q->scrolling_list(-name=>"histS2",
                            -values=>\@indexes,
                            -size=>1),
         $q->br;

   $label{'editDesc'} = 'Edit the description of query';
   print $q->radio_group(-name=>'op', -value=>"editDesc", -labels=>\%label,
			 -default=>"_",
                         -onClick=> "javascript:collapse('disp')"),
         $q->scrolling_list(-name=>"histE",
                            -values=>\@indexes,
                            -size=>1),
         $q->br;

   $label{'delete'} = 'Delete selected queries from history';
   my $size = 1;
   if ((scalar @indexes) >= 4) { $size = 4; }
   elsif ((scalar @indexes) >= 1) { $size = scalar @indexes; }
   print $q->radio_group(-name=>'op', -value=>"delete", -labels=>\%label,
			 -default=>"_",
                         -onClick=> "javascript:collapse('disp')"),
         $q->br, '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;',
         $q->scrolling_list(-name=>"histD",
                            -values=>\@indexes,
		            -multiple=>"true",
                            -size=>$size),
         $q->br;
   print '</dd>';
}
####End of subroutine print_actions

#this prints the history listing section of the form
sub print_history_section {
   print '<dt><b>Query history</b></dt>',
         '<dd>',
         #$q->start_table({rules=>"rows", bordercolor=>"#FF6666"}), "\n";
         $q->start_table, "\n";
   
   my $i = 1;
   foreach (sort bynumber keys %{$history}) {
      if ($i % 2 == 1) { print '<tr bgcolor="#FFCCCC">'; }
      else { print '<tr>'; }
      print '<td>', $_, '. ',  #undefs???
            $history->{$_}->{DESCRIPTION}, '</td>',
            '<td nowrap>(', $history->{$_}->{RESULTCOUNT}, ' alignments)</td>',
            '</tr>', "\n";
      $i++;
      #print a line between data rows
      #print '<tr><td colspan=2 cellpadding=0 cellspacing=0><hr></td></tr>', "\n";
   }
   print $q->end_table, '</dd>';
}
####End of subroutine print_history_section

######################################################################
# Subroutines for displaying form and forming query
####################################################
#subroutine to display the form for queries
sub display_form {
   #start page with cookies 
   start_html();
   print $q->start_form;
   print $q->h3("Experiment");
   print "Experiment ID or range ";
   print $q->textfield(-name=>"expt_low",
                       -size=>5,
                       -maxlength=>10);
   print '&nbsp;&nbsp;&nbsp;';
   print $q->textfield(-name=>"expt_hi",
                       -size=>5,
                       -maxlength=>10);
   print $q->br;
   print "Type ";
   my @type = @{ $dbh->selectcol_arrayref("select name from core.expttype order by name") };
   unshift(@type, ' ');
   print $q->scrolling_list(-name=>"type",
                            -values=>\@type,
                            -size=>1);
   print $q->br;
   my @lab = @{ $dbh->selectcol_arrayref("select name from core.lab order by name") };
   unshift(@lab, ' ');
   print "Lab ";
   print $q->scrolling_list(-name=>"pi",
                       -size=>1,
                       -values=>\@lab);
   print $q->br;
   print "Cell line ";
   my @cell = @{$dbh->selectcol_arrayref("select name from core.cellline order by name")};
   unshift(@cell, ' ');
   print $q->scrolling_list(-name=>"cell",
                            -values=>\@cell,
                            -multiple=>'true',
                            -style=>'width:400px;height:30px',
                            -class=>"js-basic-multiple");
   print '&nbsp;&nbsp;Condition&nbsp;';
   #can we add limit by treatment by cell line
   my @treat = @{$dbh->selectcol_arrayref("select name from core.exptcondition order by name")};
   unshift(@treat, ' ', "none");
   print $q->scrolling_list(-name=>"treat",
                            -values=>\@treat,
                            -size=>1);
   print $q->br,
         "Target (Ab versus) ";
         #"<table><tr><td valign='TOP'>Target (Ab versus) ";
   my @target = @{ $dbh->selectcol_arrayref("select name from core.expttarget order by name") };
   unshift(@target, " ");
   print $q->scrolling_list(-name=>"ltar",
                            -values=>\@target,
                            -multiple=>'true',
                            -style=>'width:400px;height:30px',
                            -class=>"js-basic-multiple");
   print $q->br, "Target with pattern matching ";
   print $q->textfield(-name=>"ltarp",
                       -size=>20,
                       -maxlength=>50),
         $q->br;
   print $q->h3("Alignment");
   #id,name,genome,permissions,aligntype,uploadstatus
   print "Alignment ID or range ";
   print $q->textfield(-name=>"aln_low",
                       -size=>5,
                       -maxlength=>10);
   print '&nbsp;&nbsp;&nbsp;';
   print $q->textfield(-name=>"aln_hi",
                       -size=>5,
                       -maxlength=>10);
   print $q->br;
   print "Name ";
   print $q->textfield(-name=>"aln_name",
                       -size=>20,
                       -maxlength=>40);
   print $q->br;
   print "Type ";
   my @type = @{ $dbh->selectcol_arrayref("select name from core.aligntype order by name") };
   unshift(@type, ' ');
   print $q->scrolling_list(-name=>"alntype",
                            -values=>\@type,
                            -size=>1);
   print $q->br;
   print "Genome ";
   my @genome = @{ $dbh->selectcol_arrayref("select version from core.genome order by version") };
   unshift(@genome, ' ');
   print $q->scrolling_list(-name=>"genome",
                            -values=>\@genome,
                            -size=>1);
   print $q->br;
   print "Upload status ";
   my @stat = @{ $dbh->selectcol_arrayref("select distinct(wiguploadstatus) from seqalignment order by wiguploadstatus") };
   unshift(@stat, ' ');
   print $q->scrolling_list(-name=>"status",
                            -values=>\@stat,
                            -size=>1);
   print $q->br;
   #string match: improvement list of permissions avail ie "public" not "public:meto"
   print "Permissions ";
   print $q->textfield(-name=>"perm",
                       -size=>20,
                       -maxlength=>40);
   print $q->br;
   print $q->br, $q->br,
         $q->submit(-name=>"mode", -value=>"Submit Query");
   print $q->end_form;
   if ($testdb) { print "Test database\n", $q->br; }
   print $q->end_html,"\n";

}
####End of subroutine display_form

#display the results section in main form and for filtering products
sub display_results_form {
   print "Assembly mapped to ";
   my @asm = @{$dbh->selectcol_arrayref("select version from genome order by version")};
   unshift(@asm, " ");
   print $q->scrolling_list(-name=>"asm",
                            -values=>\@asm,
                            -size=>1);
   print $q->br;
   print "Minimum read count ";
   print $q->textfield(-name=>"mcnt", -size=>12, -maxlength=>12);
   print $q->br;
   print "Maximum p-value ";
   print $q->textfield(-name=>"mpv", -size=>12, -maxlength=>12);
   print $q->br;
   print "Minimum fold enrichment ";
   print $q->textfield(-name=>"mfe", -size=>12, -maxlength=>12);
   print $q->br;
} 
####End of subroutine display_results_form

#subroutine to display the query string
sub display_query_string {
   print $q->header(-type=> 'text/html'),
         $q->start_html('query string'),
         $q->h2("Query String");
   foreach ($q->param) {
      print $_, '="', $q->param($_), '"<BR>', "\n";
   }
   print $q->end_html;
   if ($dbh && $dbh->{Active}) { $dbh->disconnect; }
   exit 0;
}
####End of display_query_string

#subroutine to display message that no data was found
sub print_nonefound {
   my($desc) = @_;
   start_html('Query results', 'Query results');
   print $q->h2('No data was found to match the criteria.');
   if ($desc) {
      print "Description of query: $desc\n",
            $q->br;
   }
   print $q->a({href=>$query_url}, "New query"),
         $q->end_html;
   if ($dbh && $dbh->{Active}) { $dbh->commit; $dbh->disconnect; }
   exit 0;
}
####End of subroutine print_nonefound

#subroutine to set global variables and flags
sub set_globals {
   $case_flag = 0;
   $conn = $q->param("group") if $q->param("group");
   if (! $conn) { $conn = "AND"; } #use AND as default
   if ($q->param("case") && $q->param("case") eq "Exact case") { $case_flag = 1; }
}
####End of subroutine set_globals

#subroutine to write query and put response in query string
sub write_query {
   my @sql;
   my $desc = '';
   my $line;
   my $d;
   if ($q->param("expt_low") or $q->param("expt_hi") or
       $q->param("type") or $q->param("pi") or
       $q->param("cell") or $q->param("treat") or $q->param("ltar") or
       $q->param("ltarp")
       ) {
      ($line, $d) = write_expt();
      if ($line) { push(@sql, $line); $desc .= "$d AND "; }
   }
   if ($q->param("mpv") or $q->param("mfe")) {
      ($line, $d) = write_analysis();
      if ($line) { push(@sql, $line); $desc .= "$d AND "; }
   }
   if ($q->param("genome") or $q->param("aln_name") or
       $q->param("aln_low") or $q->param("aln_hi") or
       $q->param("alntype") or $q->param("status") or
       $q->param("perm")) {
      ($line, $d) = write_seqalignment();
      if ($line) { push(@sql, $line); $desc .= "$d AND "; }
   }

   #check for "no query" / "query all"
   if (!@sql or $sql[0] eq '') {
      $sql[0] = "SELECT id from seqalignment";
      $desc = "all alignments";
   }
   my $sth;
   $dbh->{RaiseError} = 0;
   #$dbh->{PrintError} = 0;
   #write results directly into query_results
   #my $query = join("\n INTERSECT \n", @sql);
   #no intersect so use nested id in ....
   my $query = $sql[0];
   my $e = ''; #end parens
   for(my $i=1; $i<=$#sql; $i++) {
      my $t = $sql[$i];
      $t =~ s/select id/AND id in (select id/i;
      $query .= $t;
      $e .= ")";
   }
   $query .= $e;
   #send_mail("TESTING $query");
   $desc =~ s/ AND $//;
   if (length $desc > 1500) {
      $desc = substr($desc, 0, 1499);
   }
   return ($query, $desc);
}
####End of subroutine write_query

#subroutine to break up a string on AND or OR and return as a list
sub divide_string {
   my $string = shift;
   my @str = split(/\b(AND|OR)\b/i, $string);
   foreach (@str) {
      s/^\s*//;
      s/\s*$//;
   }
   #check for ending with an "and" or "or"
   if ($str[$#str] =~ /\b(AND|OR)\b/i && $str[$#str-1] !~ /\b(AND|OR)\b/i) {
      #remove hanging and/or
      pop @str;
   }
   @str;
}
####End of divide_string

#subroutine to display the query for testing purposes
sub display_query {
   my($sql, @vars) = @_;
   my(@sql) = split(/\?/, $sql);
   my($line) = shift(@sql);
   foreach (@vars) {
      $line .= " '$_' ";
      $line .= shift(@sql);
   }
   &print_error($line);
}
####End of subroutine display_query

#this sub writes the html for the expand/hide link
sub expand_hide_link {
   my $id = shift @_;
   my $link = shift @_;
   my $css_class = shift @_;
   my $list_element = shift @_;
   my $m = 'none';
   if ($id eq 'mutation' && $q->param('openMut')) {
      $m = 'block';
   }
   if (!$list_element) { 
      print "\n", '<dt>'; #indent everything under link
   }else {
      print "\n", $list_element;
   }
   if ($css_class eq 'normal') {
      print '<span>';
   }else {
      print '<span class=', $css_class, '>';
   }
   print '<a href="javascript:expand(\'', $id, '\')">', $link, 
         '</a></span><br />', "\n";
   if (!$list_element) {
      print '</dt><dd>', "\n";
   }
   print '<div id="', $id, '" style="display: ', $m, ';">', "\n";
}
####End of subroutine expand_hide_link

sub write_analysisresults {
   my $sql = 'select alignment from analysisinputs where analysis in (select analysis from analysisresults where ';
   my $desc = '';
   if ($q->param("mpv") && $q->param("mpv") ne ' ') {
      my $t = $q->param("mpv");
      $sql .= "pvalue <= ? and ";
      push(@bind_vars, $t);
      $desc .= "pvalue <= $t AND ";
   }
   if ($q->param("mfe") && $q->param("mfe") ne ' ') {
      my $t = $q->param("mfe");
      $sql .= "fold_enrichment >= ? and ";
      push(@bind_vars, $t);
      $desc .= "fold_enrichment >= $t AND ";
   }
   $sql =~ s/ and $/)/;
   if ($sql eq 'select alignment from analysisinputs where analysis in (select analysis from analysisresults where ') { undef $sql; }
   $desc =~ s/ AND $//;
   return ($sql, $desc);
}
####

sub write_seqalignment {
   my $sql = 'select id from seqalignment where ';
   my $desc = '';
   #$q->param("genome") or $q->param("aln_name") or
   #$q->param("aln_low") or $q->param("aln_hi") or
   #$q->param("alntype") or $q->param("status") or
   #$q->param("perm")

   if ($q->param("genome") && $q->param("genome") ne ' ') {
      my $t = $q->param("genome");
      my @g = $dbh->selectrow_array("select id from core.genome where version = ?", undef, $t);
      $sql .= "genome = ? and "; 
      push(@bind_vars, $g[0]);
      $desc .= "genome = $t AND ";
   }
   if ($q->param("aln_name") && $q->param("aln_name") ne '') { #free text
      my $t = '%' . $q->param("aln_name") . '%';
      $sql .= "name like ? and ";
      push(@bind_vars, $t);
      $desc .= "alignment name like " . $q->param("aln_name") . " AND ";
   }
   if ($q->param("aln_low") && $q->param("aln_low") ne '') {
      my $t = $q->param("aln_low");
      if ($q->param("aln_hi") && $q->param("aln_hi") ne '') {
         my $h = $q->param("aln_hi");
         $sql .= "id >= ? and id <= ? and ";
         push(@bind_vars, $t, $h);
         $desc .= "aln between $t and $h AND ";
      }else {
         $sql .= "id = ? and ";
         push(@bind_vars, $t);
         $desc .= "aln equals $t AND ";
      }
   }
   if ($q->param("alntype") && $q->param("alntype") ne ' ') {
      my $t = $q->param("alntype");
      my @g = $dbh->selectrow_array("select id from core.aligntype where name = ?", undef, $t);
      $sql .= "aligntype = ? and ";
      $desc .= "aligntype is $t AND ";
      push(@bind_vars, $g[0]);
   }
   if ($q->param("status") && $q->param("status") ne ' ') {
      $sql .= "wiguploadstatus = ? and ";
      $desc .= "upload status is " . $q->param("status") . " AND ";
      push(@bind_vars, $q->param("status"));
   }
   if ($q->param("perm") && $q->param("perm") ne '') { #free text
      my $p = $q->param("perm");
      $sql .= "permissions like ? and ";
      $desc .= "permissions includes $p AND ";
      push(@bind_vars, '%' . $p . '%');
   }

   #if ($q->param("mcnt") && $q->param("mcnt") ne '') {
      #need integers, check for M or m?
      #my $t = $q->param("mcnt");
      #if ($t =~ /\D/) {
         #if ($t =~ /(\d+)m$/i) { $t = $1 * 1000000; }
         #else { print_error("Number of hits needs to be an integer"); }
      #}
      #$sql .= "numhits >= ? and ";
      #push(@bind_vars, $t);
      #$desc .= "num hits >= $t AND ";
   #}

   $sql =~ s/ and $//;
   if ($sql eq 'select id from seqalignment where ') { undef $sql; }
   $desc =~ s/ AND $//;
   return ($sql, $desc);      
}
####

sub write_expt {
   my $sql = 'select id from seqalignment where expt in (select id from seqexpt where ';
   my $desc = '';
   #if ($q->param("expt_low") or $q->param("expt_hi") or
       #$q->param("type") or $q->param("pi") or
       #$q->param("cell") or $q->param("treat") or $q->param("ltar")
   #id expttype lab cellline exptcondition expttarget (all integers)

   if ($q->param("expt_low") && $q->param("expt_low") ne '') {
      my $t = $q->param("expt_low");
      if ($q->param("expt_hi") && $q->param("expt_hi") ne '') {
         my $h = $q->param("expt_hi");
         $sql .= "id >= ? and id <= ? and ";
         push(@bind_vars, $t, $h);
         $desc .= "expt between $t and $h AND ";
      }else {
         $sql .= "id = ? and ";
         push(@bind_vars, $t);
         $desc .= "expt equals $t AND ";
      }
   }
   if ($q->param("type") && $q->param("type") ne ' ') {
      my $t = $q->param("type");
      my @g = $dbh->selectrow_array("select id from core.expttype where name = ?", undef, $t);
      $sql .= "expttype = ? and ";
      $desc .= "expt type is $t AND ";
      push(@bind_vars, $g[0]);
   }
   if ($q->param("pi") && $q->param("pi") ne ' ') {
      my $t = $q->param("pi");
      my @g = $dbh->selectrow_array("select id from core.lab where name = ?", undef, $t);
      $sql .= "lab = ? and ";
      $desc .= "lab is $t AND ";
      push(@bind_vars, $g[0]);
   }
   #multiple select
   if ($q->param("cell") && $q->param("cell") ne ' ') {
      my @c = $q->param("cell");
      $sql .= "(";
      $desc .= "cell line is ";
      foreach my $t (@c) {
         my @g = $dbh->selectrow_array("select id from core.cellline where name = ?", undef, $t);
         $sql .= "cellline = ? or ";
         $desc .= "$t, ";
         push(@bind_vars, $g[0]);
      }
      $sql =~ s/or $/) and /;
      $desc =~ s/, $/ AND /;    
   }
   if ($q->param("treat") && $q->param("treat") ne ' ') {
      my $t = $q->param("treat");
      my @g = $dbh->selectrow_array("select id from core.exptcondition where name = ?", undef, $t);
      $sql .= "exptcondition = ? and ";
      $desc .= "condition is $t AND ";
      push(@bind_vars, $g[0]);
   }
   #multiple select
   if ($q->param("ltar") && $q->param("ltar") ne ' ') {
      my @tar = $q->param("ltar");
      $sql .= "(";
      $desc .= "target is ";
      foreach my $t (@tar) {
         my @g = $dbh->selectrow_array("select id from core.expttarget where name = ?", undef, $t);
         $sql .= "expttarget = ? or ";
         $desc .= "$t, ";
         push(@bind_vars, $g[0]);
      }
      $sql =~ s/or $/) and /;
      $desc =~ s/, $/ AND /;
   }elsif ($q->param("ltarp") && $q->param("ltarp") ne '') {
      my $t = $q->param("ltarp");
      $sql .= "expttarget in (select id from core.expttarget where name like ?) and ";
      push(@bind_vars, '%' . $t . '%');
      $desc .= "target like $t AND ";
   }

   $sql =~ s/ and $/)/;
   if ($sql eq 'select id from seqalignment where expt in (select id from seqexpt where ') { undef $sql; }
   $desc =~ s/ AND $//;
   return ($sql, $desc);
}
####

sub display_results {
   my $queryind = shift;
   #userid
   if ($q->param("display_format") && $q->param("display_format") eq "expts") {
      display_expt_tab($history->{$queryind}->{HISTORYID});
   }elsif ($q->param("display_format") && $q->param("display_format") eq "aligns") {
      display_align_tab($history->{$queryind}->{HISTORYID});
   }elsif ($q->param("display_format") && $q->param("display_format") eq "exptalign") {
      display_expt_align_tab($history->{$queryind}->{HISTORYID});
   }else {
      print_error("Unable to display results");
   }
}
#### 

#display fields from expt table in an html table
sub display_expt_tab {
   my $qu = shift; #historyid
   my $sth = $dbh->prepare("select * from seqexpt where id in (select expt from seqalignment where id in (select id from history.query_results where historyid = ?)) order by seqexpt.id");
   $sth->execute($qu);
   my $etype = $dbh->selectall_hashref("select id, name from core.expttype", 'ID');
   my $spec = $dbh->selectall_hashref("select id, name from core.species", 'ID');
   my $lab = $dbh->selectall_hashref("select id, name from core.lab", 'ID');
   my $cond = $dbh->selectall_hashref("select id, name from core.exptcondition", 'ID');
   my $cell = $dbh->selectall_hashref("select id, name from core.cellline", 'ID');
   my $rtype = $dbh->selectall_hashref("select id, name from core.readtype", 'ID');
   my $tar = $dbh->selectall_hashref("select id, name from core.expttarget", 'ID');
   start_html_searchpanes("Experiment table");
   print $q->br;
   print '<table id="sorttab" class="display cell-border compact">';
   #table headers
   my @head = @{$dbh->selectcol_arrayref("select column_name from information_schema.columns where table_schema = ? and table_name = ?", undef, 'seqdata', 'seqexpt')};
   print '<thead>';
   foreach (@head) { print "<th>$_</th>"; }
   print '</thead>',
         "\n";
   
   my $cnt = 0;
   while (my @row = $sth->fetchrow_array) {
      #replace ids for controlled vocab
      $row[3] = $spec->{$row[3]}{NAME};
      $row[4] = $etype->{$row[4]}{NAME};
      $row[5] = $lab->{$row[5]}{NAME};
      $row[6] = $cond->{$row[6]}{NAME};
      $row[7] = $tar->{$row[7]}{NAME};
      $row[8] = $cell->{$row[8]}{NAME};
      $row[9] = $rtype->{$row[9]}{NAME};
      print '<tr>';
      my $i = 0;
      foreach my $r (@row) {
         if ($i == 0) { #make ID a link to further details
            my $url= $query_url . "?exptpage=$r";
            $r = $q->a({href=>$url}, $r);
         }
         if (!defined $r) { $r = ''; }
         print '<td>', $r, '</td>', "\n";
         $i++;
      }
      print '</tr>', "\n";
      $cnt++;
   }
   print '</table>'; 
   if ($cnt == 0) { print "None found"; }
   #else { print "Found $cnt experiments\n"; } 
   print $q->end_html,"\n";
}
####

#display table with both experiment and alignment table fields
sub display_expt_align_tab {
   my $qu = shift; #historyid
   my $sth = $dbh->prepare("select seqexpt.*, seqalignment.* from seqexpt, seqalignment where seqexpt.id = seqalignment.expt and seqexpt.id in (select expt from seqalignment where id in (select id from history.query_results where historyid = ?)) order by seqexpt.id");
   $sth->execute($qu);
   my $etype = $dbh->selectall_hashref("select id, name from core.expttype", 'ID');
   my $spec = $dbh->selectall_hashref("select id, name from core.species", 'ID');
   my $lab = $dbh->selectall_hashref("select id, name from core.lab", 'ID');
   my $cond = $dbh->selectall_hashref("select id, name from core.exptcondition", 'ID');
   my $cell = $dbh->selectall_hashref("select id, name from core.cellline", 'ID');
   my $rtype = $dbh->selectall_hashref("select id, name from core.readtype", 'ID');
   my $tar = $dbh->selectall_hashref("select id, name from core.expttarget", 'ID');
   my $genome = $dbh->selectall_hashref("select id, version from core.genome", 'ID');
   my $atype = $dbh->selectall_hashref("select id, name from core.aligntype", 'ID');
   start_html_searchpanes("Experiment and alignment table");
   print $q->br;
   print '<table id="sorttab" class="display cell-border compact">';
   #table headers
   my @head = @{$dbh->selectcol_arrayref("select column_name from information_schema.columns where table_schema = ? and (table_name = ? or table_name = ?) order by table_name desc, ordinal_position", undef, 'seqdata', 'seqexpt', 'seqalignment')};
   my @tab = qw(seqexpt seqalignment);
   #order of columns
   print '<thead>';
   foreach (@head) { 
      if (/^id$/) { my $t = shift @tab; $_ = "$t id"; } 
      print "<th>$_</th>"; 
   }
   print '</thead>',
         "\n";
   
   my $cnt = 0;
   while (my @row = $sth->fetchrow_array) {
      #replace ids for controlled vocab (17 columns)
      $row[3] = $spec->{$row[3]}{NAME};
      $row[4] = $etype->{$row[4]}{NAME};
      $row[5] = $lab->{$row[5]}{NAME};
      $row[6] = $cond->{$row[6]}{NAME};
      $row[7] = $tar->{$row[7]}{NAME};
      $row[8] = $cell->{$row[8]}{NAME};
      $row[9] = $rtype->{$row[9]}{NAME};
      #replace ids in alignment table also
      $row[20] = $genome->{$row[20]}{VERSION};
      $row[22] = $atype->{$row[22]}{NAME};
      print '<tr>';
      my $i = 0;
      foreach my $r (@row) {
         if ($i == 0) { #make ID a link to further details
            my $url= $query_url . "?exptpage=$r";
            $r = $q->a({href=>$url}, $r);
         }
         if ($i == 17) { #alignment ID
            my $url = $query_url .  "?alnpage=$r";
            $r = $q->a({href=>$url}, $r);
         }
         if (!defined $r) { $r = ''; }
         print '<td>', $r, '</td>', "\n";
         $i++;
      }
      print '</tr>', "\n";
      $cnt++;
   }
   print '</table>'; 
   if ($cnt == 0) { print "None found"; }
   #else { print "Found $cnt alignments\n"; } 
   print $q->end_html,"\n";
}
#### End display_expt_align_tab

#display fields from seqalignment table in an html table
sub display_align_tab {
   my $qu = shift; #historyid
   my $genome = $dbh->selectall_hashref("select id, version from core.genome", 'ID');
   my $atype = $dbh->selectall_hashref("select id, name from core.aligntype", 'ID');
   my $sth = $dbh->prepare("select * from seqalignment where id in (select id from history.query_results where historyid = ?) order by id");
   $sth->execute($qu);
   start_html_searchpanes("Alignment table");
   print $q->br;
   print '<table id="sorttab" class="display cell-border compact">';
   #table headers
   my @head = @{$dbh->selectcol_arrayref("select column_name from information_schema.columns where table_schema = ? and table_name = ?", undef, 'seqdata', 'seqalignment')};
   print '<thead>';
   foreach (@head) { print "<th>$_</th>"; }
   print '</thead>',
         "\n";
   my $cnt = 0;
   while (my @row = $sth->fetchrow_array) {
      print '<tr>';
      $row[3] = $genome->{$row[3]}{VERSION};
      $row[5] = $atype->{$row[5]}{NAME};
      my $i = 0;
      foreach my $r (@row) {
         if ($i == 0) { #link
            my $url = $query_url . "?alnpage=$r";
            $r = $q->a({href=>$url}, $r);
         }
         if (!defined $r) { $r = ''; }
         print '<td>', $r, '</td>', "\n";
         $i++;
      }
      print '</tr>', "\n";
      $cnt++;
   }
   print '</table>'; 
   if ($cnt == 0) { print "None found"; }
   #else { print "Found $cnt alignments\n"; } 
   print $q->end_html,"\n";
}
####

#display the details of a alignment, including expt and analysis
sub display_align_detail {
   my $id = shift;
   my @aln = @{$dbh->selectrow_arrayref("select * from seqalignment where id = ?", undef, $id)};
   my @expt = @{$dbh->selectrow_arrayref("select * from seqexpt where id = ?", undef, $aln[1])};
   my $anaType = $dbh->selectall_hashref("select id, name from analysistype", 'ID');
   my $genome = $dbh->selectall_hashref("select id, version from core.genome", 'ID');
   my $atype = $dbh->selectall_hashref("select id, name from core.aligntype", 'ID');
   my $etype = $dbh->selectall_hashref("select id, name from core.expttype", 'ID');
   my $spec = $dbh->selectall_hashref("select id, name from core.species", 'ID');
   my $lab = $dbh->selectall_hashref("select id, name from core.lab", 'ID');
   my $cond = $dbh->selectall_hashref("select id, name from core.exptcondition", 'ID');
   my $cell = $dbh->selectall_hashref("select id, name from core.cellline", 'ID');
   my $rtype = $dbh->selectall_hashref("select id, name from core.readtype", 'ID');
   my $tar = $dbh->selectall_hashref("select id, name from core.expttarget", 'ID');
   my $isth = $dbh->prepare("select * from analysisinputs where alignment = ?");
   my $asth = $dbh->prepare("select * from seqdataanalysis where id = ?");
   my $hsth = $dbh->prepare("select column_name from information_schema.columns where table_schema = 'seqdata' and table_name = ? order by ordinal_position");
   start_html("Alignment detail page");
   print $q->br, $q->br;
   print $q->strong("Alignment $aln[0]"), $q->br;
   my @head = @{$dbh->selectcol_arrayref($hsth, undef, 'seqalignment')};
   $aln[3] = $genome->{$aln[3]}{VERSION};
   $aln[5] = $atype->{$aln[5]}{NAME};
   for(my $i = 2; $i < $#aln; $i++) {
      print "$head[$i]: $aln[$i]", $q->br;
   }
   print "\n"; #readablility
   print '<br>',
         $q->start_form(),
         '<input type="hidden" name="alnpage" value=', $id, '>',
         '<input type="submit" name="mode" value="Edit this alignment">',
         '</form><br>';
   if ($testdb) { print "Test database\n", $q->br; }
   print $q->br;
   print $q->strong("Experiment $aln[1]"), $q->br;
   @head = @{$dbh->selectcol_arrayref($hsth, undef, 'seqexpt')};
   #replace ids to controlled vocab
   $expt[3] = $spec->{$expt[3]}{NAME};
   $expt[4] = $etype->{$expt[4]}{NAME};
   $expt[5] = $lab->{$expt[5]}{NAME};
   $expt[6] = $cond->{$expt[6]}{NAME};
   $expt[7] = $tar->{$expt[7]}{NAME};
   $expt[8] = $cell->{$expt[8]}{NAME};
   $expt[9] = $rtype->{$expt[9]}{NAME};
   for(my $i = 1; $i < $#expt; $i++) {
      print "$head[$i]: $expt[$i]", $q->br;
   }
   print "\n"; #readablility
   print $q->br;
   #allow to edit experiment?
   print '<br>',
         $q->start_form(),
         '<input type="hidden" name="exptpage" value=', $aln[1], '>',
         '<input type="submit" name="mode" value="Edit this experiment">',
         '</form><br><br>';
   if ($testdb) { print "Test database\n", $q->br; }
   print $q->strong("Analysis"), $q->br; #these tables are empty so far
   $isth->execute($aln[0]);
   while (my @inp = $isth->fetchrow_array) {
      print "$inp[2]:", $q->br;
      @head = @{$dbh->selectcol_arrayref($hsth, undef, 'seqdataanalysis')};
      $asth->execute($inp[0]);
      my @ana = $asth->fetchrow_array; #can there be more than 1????
      for(my $i = 1; $i < $#head; $i++) {
         if ($i == 1) { $ana[$i] = $anaType->{$ana[$i]}{NAME}; }
         print "$head[$i]: $ana[$i]", $q->br;
      }
      $asth->finish;
      print "\n"; #readablility
   }
   print $q->end_html;
}
####

#display an alignment, expt, and analysis and allow editing
#hardcode database columns
sub edit_align {
   my $id = shift;
   my @aln = @{$dbh->selectrow_arrayref("select * from seqalignment where id = ?", undef, $id)};
   my @expt = @{$dbh->selectrow_arrayref("select * from seqexpt where id = ?", undef, $aln[1])};
   my $anaType = $dbh->selectall_hashref("select id, name from analysistype", 'ID');
   my $genome = $dbh->selectall_hashref("select id, version from core.genome", 'ID');
   my $atype = $dbh->selectall_hashref("select id, name from core.aligntype", 'ID');
   my $etype = $dbh->selectall_hashref("select id, name from core.expttype", 'ID');
   my $spec = $dbh->selectall_hashref("select id, name from core.species", 'ID');
   my $lab = $dbh->selectall_hashref("select id, name from core.lab", 'ID');
   my $cond = $dbh->selectall_hashref("select id, name from core.exptcondition", 'ID');
   my $cell = $dbh->selectall_hashref("select id, name from core.cellline", 'ID');
   my $rtype = $dbh->selectall_hashref("select id, name from core.readtype", 'ID');
   my $tar = $dbh->selectall_hashref("select id, name from core.expttarget", 'ID');
   my $isth = $dbh->prepare("select * from analysisinputs where alignment = ?");
   my $asth = $dbh->prepare("select * from seqdataanalysis where id = ?");
   my $hsth = $dbh->prepare("select column_name from information_schema.columns where table_schema = 'seqdata' and table_name = ? order by ordinal_position");
   start_html("Alignment edit page");
   print $q->start_form;
   print $q->br, $q->br;
   #don't edit alignment or experiment ids
   print $q->strong("Alignment $aln[0]"), $q->br;
   my @head = @{$dbh->selectcol_arrayref($hsth, undef, 'seqalignment')};
   for(my $i = 2; $i <= $#aln; $i++) {
      if ($head[$i] eq 'genome') { #do not allow editing here
         print "$head[$i]: ", $genome->{$aln[$i]}{VERSION}, 
               $q->br;
      #}elsif ($head[$i] eq 'permissions') { #do not allow editing here
         #print "$head[$i]: $aln[$i]", $q->br;
      }elsif ( $head[$i] eq 'aligntype') { #scrolling list
         my @t;
         foreach my $k (keys %$atype) { push(@t, $atype->{$k}{NAME}); }
         print "$head[$i]: ",
               $q->scrolling_list(-name=>"$head[$i]",
                        -default=>"$atype->{$aln[$i]}{NAME}",
                        -size=>1,
                        -values=>\@t),
               $q->br;
      }else { #text box
         print "$head[$i]: ", 
               $q->textfield(-name=>"$head[$i]",
                        -value=>"$aln[$i]",
                        -size=>60,
                        -maxlength=>255);
         print $q->br;
      }
      print "\n";
   }
   print "\n"; #readablility
   #do experiment and analysis separately
   if (0) {
   print $q->strong("Analysis"), $q->br; #these tables are empty so far
   $isth->execute($aln[0]); #analysis(id), alignment(id), inputtype
   while (my @inp = $isth->fetchrow_array) {
      print "$inp[2]:", $q->br;
      #id*,type*,name,version,program,active  *id
      @head = @{$dbh->selectcol_arrayref($hsth, undef, 'seqdataanalysis')};
      $asth->execute($inp[0]);
      my @ana = $asth->fetchrow_array; #can there be more than 1????
      for(my $i = 1; $i < $#head; $i++) {
         if ( $head[$i] eq 'type') {
            my @t;
            foreach my $k (keys %$anaType) { push(@t, $anaType->{$k}{NAME}); }
            print "$head[$i]: ",
               $q->scrolling_list(-name=>"$head[$i]",
                        -default=>"$anaType->{$ana[$i]}{NAME}",
                        -size=>1,
                        -values=>\@t),
               $q->br;
         }elsif ( $head[$i] eq 'active') {
            print "$head[$i]: ",
               $q->scrolling_list(-name=>"$head[$i]",
                        -default=>$ana[$i],
                        -size=>1,
                        -values=>\[0, 1]),
               $q->br;
         }else { #text box
            print "$head[$i]: ",
               $q->textfield(-name=>"$head[$i]",
                        -value=>"$ana[$i]",
                        -size=>60,
                        -maxlength=>200);
            print $q->br;
         }
         print "\n";

         if ($i == 1) { $ana[$i] = $anaType->{$ana[$i]}{NAME}; }
         print "$head[$i]: $ana[$i]", $q->br;
      }
      $asth->finish;
      print "\n"; #readablility
   }
   }#comment out
   #needs a button and subroutine to write to the database
   print $q->br, $q->hidden(-name=>"tab", -value=>"seqalignment");
   print $q->hidden(-name=>"id", -value=>"$aln[0]");
   print $q->submit(-name=>"mode", -value=>"Save");
   print $q->end_form;
   if ($testdb) { print "Test database\n", $q->br; }
   print $q->end_html;
}
####

sub edit_expt {
   my $id = shift;
   my @expt = @{$dbh->selectrow_arrayref("select * from seqexpt where id = ?", undef, $id)};
   my $genome = $dbh->selectall_hashref("select id, version from core.genome", 'ID');
   my $etype = $dbh->selectall_hashref("select id, name from core.expttype", 'ID');
   my $spec = $dbh->selectall_hashref("select id, name from core.species", 'ID');
   my $lab = $dbh->selectall_hashref("select id, name from core.lab", 'ID');
   my $cond = $dbh->selectall_hashref("select id, name from core.exptcondition", 'ID');
   my $cell = $dbh->selectall_hashref("select id, name from core.cellline", 'ID');
   my $rtype = $dbh->selectall_hashref("select id, name from core.readtype", 'ID');
   my $tar = $dbh->selectall_hashref("select id, name from core.expttarget", 'ID');
   my $hsth = $dbh->prepare("select column_name from information_schema.columns where table_schema = 'seqdata' and table_name = ? order by ordinal_position");
   start_html("Experiment edit page");
   print $q->br, $q->br;
   print $q->start_form;
   #don't edit experiment ids
   print $q->strong("Experiment $id"), $q->br;
   my @head = @{$dbh->selectcol_arrayref($hsth, undef, 'seqexpt')};
   for(my $i = 1; $i <= $#head; $i++) {
      if ( $head[$i] eq 'name') { #not edited directly composite of other fields
         print "name: $expt[$i]", $q->br;
      }elsif ( $head[$i] eq 'species') { #scrolling list
         #not edit species???
         print "$head[$i]: $spec->{$expt[$i]}{NAME}", $q->br;
         #my @t;
         #foreach my $k (keys %$spec) { push(@t, $spec->{$k}{NAME}); }
         #print "$head[$i]: ",
               #$q->scrolling_list(-name=>"$head[$i]",
                        #-default=>"$spec->{$expt[$i]}{NAME}",
                        #-size=>1,
                        #-values=>\@t),
               #$q->br;
      }elsif ( $head[$i] eq 'cellline') { 
         my @t;
         foreach my $k (keys %$cell) { push(@t, $cell->{$k}{NAME}); }
         print "$head[$i]: ",
               $q->scrolling_list(-name=>"$head[$i]",
                        -default=>"$cell->{$expt[$i]}{NAME}",
                        -size=>1,
                        -values=>\@t),
               $q->br;
      }elsif ( $head[$i] eq 'expttype') {
         my @t;
         foreach my $k (keys %$etype) { push(@t, $etype->{$k}{NAME}); }
         print "$head[$i]: ",
               $q->scrolling_list(-name=>"$head[$i]",
                        -default=>"$etype->{$expt[$i]}{NAME}",
                        -size=>1,
                        -values=>\@t),
               $q->br;
      }elsif ( $head[$i] eq 'lab') {
         my @t;
         foreach my $k (keys %$lab) { push(@t, $lab->{$k}{NAME}); }
         print "$head[$i]: ",
               $q->scrolling_list(-name=>"$head[$i]",
                        -default=>"$lab->{$expt[$i]}{NAME}",
                        -size=>1,
                        -values=>\@t),
               $q->br;
      }elsif ( $head[$i] eq 'exptcondition') {
         my @t;
         foreach my $k (keys %$cond) { push(@t, $cond->{$k}{NAME}); }
         print "$head[$i]: ",
               $q->scrolling_list(-name=>"$head[$i]",
                        -default=>"$cond->{$expt[$i]}{NAME}",
                        -size=>1,
                        -values=>\@t),
               $q->br;
      }elsif ( $head[$i] eq 'expttarget') {
         my @t;
         foreach my $k (keys %$tar) { push(@t, $tar->{$k}{NAME}); }
         print "$head[$i]: ",
               $q->scrolling_list(-name=>"$head[$i]",
                        -default=>"$tar->{$expt[$i]}{NAME}",
                        -size=>1,
                        -values=>\@t),
               $q->br;
      }elsif ( $head[$i] eq 'readtype') {
         my @t;
         foreach my $k (keys %$rtype) { push(@t, $rtype->{$k}{NAME}); }
         print "$head[$i]: ",
               $q->scrolling_list(-name=>"$head[$i]",
                        -default=>"$rtype->{$expt[$i]}{NAME}",
                        -size=>1,
                        -values=>\@t),
               $q->br;
      #possible TODO is to add exptnote as a file upload (up to 4G text?)
      # or at least a text area
      }else { #text box
         print "$head[$i]: ",
               $q->textfield(-name=>"$head[$i]",
                        -value=>"$expt[$i]",
                        -size=>60,
                        -maxlength=>500); #500 for fqfile
         print $q->br;
      }
      print "\n";
   }
   print "\n"; #readablility
   #needs a button and subroutine to write to the database
   print $q->hidden(-name=>"tab", -value=>"seqexpt");
   print $q->hidden(-name=>"id", -value=>"$expt[0]");
   print $q->submit(-name=>"mode", -value=>"Save");
   print $q->end_form;
   if ($testdb) { print "Test database\n", $q->br; }
   print $q->end_html;
}
####

#details for an experiment, including list of alignments
sub display_expt_detail {
   my $id = shift;
   my @expt = @{$dbh->selectrow_arrayref("select * from seqexpt where id = ?", undef, $id)};
   my $asth = $dbh->prepare("select * from seqalignment where expt = ?");
   my $hsth = $dbh->prepare("select column_name from information_schema.columns where table_schema = 'seqdata' and table_name = ? order by ordinal_position");
   my $genome = $dbh->selectall_hashref("select id, version from core.genome", 'ID');
   my $atype = $dbh->selectall_hashref("select id, name from core.aligntype", 'ID');
   my $etype = $dbh->selectall_hashref("select id, name from core.expttype", 'ID');
   my $spec = $dbh->selectall_hashref("select id, name from core.species", 'ID');
   my $lab = $dbh->selectall_hashref("select id, name from core.lab", 'ID');
   my $cond = $dbh->selectall_hashref("select id, name from core.exptcondition", 'ID');
   my $cell = $dbh->selectall_hashref("select id, name from core.cellline", 'ID');
   my $rtype = $dbh->selectall_hashref("select id, name from core.readtype", 'ID');
   my $tar = $dbh->selectall_hashref("select id, name from core.expttarget", 'ID');
   start_html("Experiment detail page");
   print $q->br, $q->br;
   print $q->strong("Experiment $id"), $q->br;
   my @head = @{$dbh->selectcol_arrayref($hsth, undef, 'seqexpt')};
   #replace ids to controlled vocab
   $expt[3] = $spec->{$expt[3]}{NAME};
   $expt[4] = $etype->{$expt[4]}{NAME};
   $expt[5] = $lab->{$expt[5]}{NAME};
   $expt[6] = $cond->{$expt[6]}{NAME};
   $expt[7] = $tar->{$expt[7]}{NAME};
   $expt[8] = $cell->{$expt[8]}{NAME};
   $expt[9] = $rtype->{$expt[9]}{NAME};
   for(my $i = 1; $i < $#expt; $i++) {
      print "$head[$i]: $expt[$i]", $q->br;
   }
   print "\n"; #readablility
   print '<br>',
         $q->start_form(),
         '<input type="hidden" name="exptpage" value=', $id, '>',
         '<input type="submit" name="mode" value="Edit this experiment">',
         '</form><br>';
   if ($testdb) { print "Test database\n", $q->br; }
   print $q->br, $q->strong("Alignments:"), $q->br;
   @head = @{$dbh->selectcol_arrayref($hsth, undef, 'seqalignment')};
   splice(@head, 1, 1);  #remove expt id
   print $q->start_table({-border=>1});
   print '<thead>';
   foreach (@head) { print "<th>$_</th>"; }
   print '</thead>', "\n";
   $asth->execute($id);
   while (my @row = $asth->fetchrow_array) {
      splice(@row, 1, 1); #remove expt id
      #replace ids to controlled vocab, HARDCODED column positions
      $row[2] = $genome->{$row[2]}{VERSION};
      $row[4] = $atype->{$row[4]}{NAME};
      print '<tr>';
      foreach(@row) { print "<td>$_</td>"; }
      print '</tr>';
      print "\n";
   }
   #Edit
   print $q->end_table;
   print $q->end_html;
}
####

#no quality metrics available currently, hlab version left for future reference
#display a table of quality metrics for multiple IDs
sub display_quality_table {
   my $qu = shift; #historyid
   my $sth = $dbh->prepare("select id, description, size_in_bp, type from library where id in (select id from history.query_results where historyid = ?) order by id");

   $sth->execute($qu);
   my $sth2 = $dbh->prepare("select prid, description, num_mapped_reads, num_reads, filtered_reads, assembly from product where id = ?");
   if ($q->param("filt")) {
      $sth2 = $dbh->prepare("select prid, description, num_mapped_reads, num_reads, filtered_reads, assembly from product where id = ? and prid in (select prid from filtered_product)");
   }
   my $qsth = $dbh->prepare("select * from quality where prid = ?");
   my $msth = $dbh->prepare("select distinct multiprid from multiproductlibs where subprid in (select prid from product where id = ?) UNION select distinct multiprid from multiproductlibs where subprid in (select multiprid from multiproductlibs where subprid in (select prid from product where id = ?))");
   if ($q->param("filt")) {
      $msth = $dbh->prepare("select distinct multiprid from multiproductlibs where multiprid in (select prid from filtered_product) and subprid in (select prid from product where id = ?) UNION select distinct multiprid from multiproductlibs where multiprid in (select prid from filtered_product) and subprid in (select multiprid from multiproductlibs where subprid in (select prid from product where id = ?))");
   }
   my $msth2 = $dbh->prepare("select prid, description, num_mapped_reads, num_reads, filtered_reads, assembly from multiProduct where prid = ?");
   my $sth3;
   start_html("Quality metrics table");
   #button to filter products for this query
   if (!$q->param("filt")) { #pass forward choices made from history page
      print $q->start_form();
      foreach my $k ($q->param) {
         if ($k ne "mode") {
            print $q->hidden($k, $q->param($k));
         }
      }
      print $q->submit(-name=>"mode", -value=>"Filter products");
      print $q->end_form, "\n";
   }
   print '<table id="sorttab" class="display cell-border compact">';
   #headers? ID description prid:description qualtity_table_8
   #perc_gc dup_level complexity perc_mapped NSC RSC FRIP perc_rRNA 
   print '<thead><tr><th>Library ID</th><th>Type</th><th>Description</th><th>Average fragment size</th><th>Product</th>',
         '<th>Number of reads</th><th>Number of mapped reads</th>',
         '<th>Number of filtered reads</th>',
         '<th>Percent GC</th><th>Duplication level</th>',
         '<th>Percent of seqs remaining if deduplicated</th><th>Complexity</th>',
         '<th>Percent mapped</th><th>NSC</th><th>RSC</th><th>QTag</th>',
         '<th>FRIP | FRIT</th>',
         '<th>Fraction of genome in peaks</th>',
         '<th>Percent rRNA</th><th>Number of expressed genes</th>',
         '<th>Number of reads mapped to spike-ins</th>',
         '<th>Strand specificity</th>',
         '<th>Spearman corr</th><th>MAD</th>',
         '</tr></thead><tbody>', "\n";
   my $cnt = 0;
   while (my @row = $sth->fetchrow_array) {
      my $startText = '<tr><td>';
      my $url = $query_url . "?libpage=$row[0]";
      my $col1 = $q->a({href=>$url}, $row[0]);
      $startText .= $q->a({href=>$url}, $row[0]) . '</td>';
      $startText .= '<td>' . $row[3] . '</td>';
      #print $q->a({href=>$url}, $row[0]), '</td>';
      if (!defined $row[1]) { $row[1] = '&nbsp;'; }
      $startText .=  '<td>' . $row[1] . '</td>';
      #print '<td>', $row[1], '</td>';
      if (!defined $row[2]) { $row[2] = '&nbsp;'; }
      $startText .=  '<td>' . $row[2] . '</td>';
      my $start = 1; #have start columns
      #fetch products
      $sth2->execute($row[0]);
      while (my @prow = $sth2->fetchrow_array) {
         #fetch quality scores
         $qsth->execute($prow[0]);
         my @q = $qsth->fetchrow_array;
         $qsth->finish;
         if ($start == 0) { print "<tr><td>$col1</td><td>$row[3]</td><td>$row[1]</td><td>$row[2]</td>"; }
         elsif ($start == 1) { print $startText; }
         if (!defined $prow[1]) { $prow[1] = ''; }
         if ($prow[5]) { 
            print '<td>', "$prow[0], $prow[5]: $prow[1]", '</td>';
         }else {
            print '<td>', "$prow[0]: $prow[1]", '</td>';
         }
         if ($prow[3]) { print '<td>', commify($prow[3]), '</td>'; }
         else { print '<td>&nbsp;</td>'; }
         if ($prow[2]) { print '<td>', commify($prow[2]), '</td>'; }
         else { print '<td>&nbsp;</td>'; }
         if ($prow[4]) { print '<td>', commify($prow[4]), '</td>'; }
         else { print '<td>&nbsp;</td>'; }
         #print quality scores
         #add QTag
         if (@q && defined $q[7]) {
            if ($q[7] < .25) { splice(@q, 8, 0, -2); }
            elsif ($q[7] < .5) { splice(@q, 8, 0, -1); }
            elsif ($q[7] < 1) { splice(@q, 8, 0, 0); }
            elsif ($q[7] < 1.5) { splice(@q, 8, 0, 1); }
            elsif ($q[7] >= 1.5) { splice(@q, 8, 0, 2); }
            else { splice(@q, 8, 0, '&nbsp;'); }
         }elsif (@q) {
            splice(@q, 8, 0, '&nbsp;');
         }
         if (@q) {
            shift @q; #remove id
            #put fraction of genome next to frip
            my $fr = splice(@q, 15, 1);
            splice(@q, 9, 0, $fr);
            foreach (@q) { if (!defined) { $_ = '&nbsp;'; }elsif (/^\d+$/) { $_ = commify($_); } print "<td>$_</td>"; }
         }else { #print blanks for quality
            #HARDCODED number of columns!
            for(my $i=1; $i<=16; $i++) { print '<td>&nbsp;</td>'; }
         }
         print '</tr>', "\n";
         $start = 0;
      }
      #fetch multiproducts
      my $mid = $dbh->selectcol_arrayref($msth, undef, $row[0], $row[0]);
      foreach my $m (@$mid) {
         $msth2->execute($m);
         my @mrow = $msth2->fetchrow_array;
         $msth2->finish;
         if ($start == 0) { print "<tr><td>$col1</td><td>$row[3]</td><td>$row[1]</td><td>$row[2]</td>"; }
         elsif ($start == 1) { print $startText; }
         if ($mrow[5]) { 
             print '<td>', "$mrow[0], $mrow[5]: $mrow[1]", '</td>';
         }else {
             print '<td>', "$mrow[0]: $mrow[1]", '</td>';
         }
         if ($mrow[3]) { print '<td>', commify($mrow[3]), '</td>'; }
         else { print '<td>&nbsp;</td>'; }
         if ($mrow[2]) { print '<td>', commify($mrow[2]), '</td>'; }
         else { print '<td>&nbsp;</td>'; }
         if ($mrow[4]) { print '<td>', commify($mrow[4]), '</td>'; }
         else { print '<td>&nbsp;</td>'; }
         #fetch quality scores
         $qsth->execute($m);
         my @q = $qsth->fetchrow_array;
         $qsth->finish;
         shift @q; #remove id
         if (@q) {
            #add Qtag column
            splice(@q, 7, 0, '&nbsp;'); #id removed earlier
            #put fraction of genome next to frip
            my $fr = splice(@q, 15, 1);
            splice(@q, 8, 0, $fr);

            foreach (@q) { if (!defined) { $_ = '&nbsp;'; }elsif (/^\d+$/) { $_ = commify($_); }  print "<td>$_</td>"; }
         }else {
            #HARDCODED number of columns!
            for(my $i=1; $i<=16; $i++) { print '<td>&nbsp;</td>'; }
         }
         print '</tr>', "\n";
         $start = 0;
      }
      $cnt++;
      #if ($start == 1) { #no products add blank columns
         #print '<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>';
      #}
   }
   print '</tbody></table>';
   if ($cnt == 0) { print "None found", $q->br; }
   #else { print "Found $cnt alignments\n", $q->br; }
   print $q->end_html,"\n";
}
#### 

#display a summary of the QC scores at product level (not multiproducts)
sub display_quality_summary {
   my $qu = shift; #historyid
   #hardcoded list of columns so no sql injection possible
   my @col = qw(num_reads num_mapped_reads filtered_reads perc_gc dup_level complexity perc_mapped frip fraction_peaks perc_rRNA num_xgenes);
   my @lab = ("Number of reads", "Number of mapped reads", "Number of filtered reads", "Percent GC", "Duplication level", "Complexity", "Percent mapped", "FRIP", "Fraction of genome in peaks", "Percent rRNA", "Number of expressed genes");
   my $sth;
   start_html("Quality metrics summary");
   print "<style>td { padding:5px; }</style>\n";
   print "<table><tr><th>Metric</th><th>N</th><th>min</th><th>max</th><th>ave</th></tr>\n";
   #foreach metric compute: n, min, max, ave : add median after upgrade??
   my $i = 0;
   foreach my $c (@col) {
      $sth = $dbh->prepare("select count($c), min($c), max($c), avg($c) from product, quality where id in (select id from history.query_results where historyid = ?) and product.prid = quality.prid and $c is not NULL");
      $sth->execute($qu);
      my @row = $sth->fetchrow_array;
      $sth->finish; #should only be 1
      #print results for all metrics with n > 0
      if (@row && $row[0] > 0) {
         print "<tr><td>$lab[$i]</td>";
         foreach my $f (@row) { 
             $f = commify($f);
             print "<td>$f</td>";
         }
         print "</tr>\n";
      }
      $i++;
   }
   #add fragment size from library table
   my $c = 'size_in_bp';
   my $l = 'Fragment size';
   $sth = $dbh->prepare("select count($c), min($c), max($c), avg($c) from library where id in (select id from history.query_results where historyid = ?) and $c is not nULL");
   $sth->execute($qu);
   my @row = $sth->fetchrow_array;
   $sth->finish; #should only be 1
   #print results for all metrics with n > 0
   if (@row && $row[0] > 0) {
      print "<tr><td>$l</td>";
      foreach my $f (@row) {
          $f = commify($f);
          print "<td>$f</td>";
      }
      print "</tr>\n";
   }
   print "</table>";
   print $q->end_html,"\n";
}
####

sub edit_tab_form {
   #start page with cookies
   start_html();
   print $q->start_form;
   print '<h3>Edit tables</h3>';
   print 'Choose table to edit ', $q->br;
   #my @tab = qw(seqalignment seqexpt lab cellline exptcondition expttarget);
   my @tab = qw(lab cellline exptcondition expttarget);
   foreach my $t (@tab) {
      my $s = 'core';
      if ($t eq 'seqalignment' || $t eq 'seqexpt') { $s = 'seqdata'; }
      #safe because hard coded, not user input
      my $href = $dbh->selectall_hashref("select id, name from $s.$t", 'ID');
      my %label;
      my @id = keys %$href;
      foreach my $i (@id) { $label{$i} = "$href->{$i}{ID} $href->{$i}{NAME}"; }
      if ($s eq 'core') { #allow new on core tables
         unshift(@id, 0);
         $label{0} = "new entry";
      }
      print '<input type="radio" name="etab" value="', $t, '">', $t,
            '&nbsp;&nbsp; ID ',
            $q->scrolling_list(-name=>"$t.id",
                            -values=>\@id,
                            -labels=>\%label,
                            -style=>'width:400px;height:30px',
                            -class=>"js-basic-multiple"),
            $q->br;
   }
   print $q->br;
   print $q->submit(-name=>"mode", -value=>"Edit");
   if ($testdb) { print "Test database\n", $q->br; }
   print $q->end_form,
         $q->end_html;
}
####

sub edit_core {
   my $id = shift;
   my $tab = shift; #not user input
   start_html();
   my @core;
   if ($id > 0) { 
      @core = $dbh->selectrow_array("select * from core.$tab where id = ?", undef, $id); 
      if (!@core) { print_error("Unable to find $tab $id"); }
      print "<h3>Edit $tab $id</h3>";
   }else {
      print "<h3>Add $tab</h3>";
      $core[1] = "$tab name";
   }
   print $q->start_form;
   print $q->textfield(-name=>"name", -size=>30, -value=>$core[1]);
   print $q->hidden(-name=>"id", -value=>$id);
   print $q->hidden(-name=>"tab", -value=>$tab);
   print $q->submit(-name=>"mode", -value=>"Save");
   if ($testdb) { print "Test database\n", $q->br; }
   print $q->end_form;
   print $q->end_html;
}
####

sub save_core {
   my $tab = shift; #not user input
   my $id = $q->param("id");
   my $name = $q->param("name");
   if ($id =~ /\D/) { print_error("Bad id $id"); }
   if (length $name > 200) { print_error("Name is too long $name"); }
   if ($id > 0) { #editing
      my @ch = $dbh->selectrow_array("select * from core.$tab where id = ?", undef, $id);
      if (!@ch) { print_error("ID $id does not exist"); }
      if ($ch[1] eq $name) { print_error("No change was made"); }
      #passed checks now update table
      $dbh->do("update core.$tab set name = ? where id = ?", undef, $name, $id);
   }else { #adding new
      my @ch = $dbh->selectrow_array("select * from core.$tab where name = ?", undef, $name);
      if (@ch) { print_error("Name $name already exists"); }
      $dbh->do("insert into core.$tab (name) values (?)", undef, $name);
   }
}
####

sub save_align {
   my $id = shift;
   if ($id =~ /\D/) { print_error("Bad id $id"); }
   my @ch = $dbh->selectrow_array("select * from seqalignment where id = ?", undef, $id);
   if (!@ch) { print_error("ID $id does not exist"); }
   my @bind;
   my $set = ''; #set field = ? foreach changed value
   if ($q->param("name") && $q->param("name") ne '' && $q->param("name") ne $ch[2]) {
      #free text, 200 char limit
      my $n = $q->param("name");
      if (length $n > 200) { print_error("The name is too long, $n"); }
      $set .= "name = ?, ";
      push(@bind, $n);
   }
   if ($q->param("aligntype") && $q->param("aligntype") ne '') {
      #controlled vocab, int into another table
      my $n = $q->param("aligntype");
      my @t = $dbh->selectrow_array("select id from core.aligntype where name = ?", undef, $n);
      if (!@t) { print_error("Not a valid aligntype $n"); }
      if ($t[0] ne $ch[3]) {
         push(@bind, $t[0]);
         $set .= "aligntype = ?, "
      }
   }
   if (defined $q->param("numhits") && $q->param("numhits") ne '' && $q->param("numhits") ne $ch[4]) {
      #free text, should be integer
      my $n = $q->param("numhits");
      if ($n =~ /\D/) { print_error("numhits should be an integer, $n"); }
      $set .= "numhits = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("totalweight") && $q->param("totalweight") ne '' && $q->param("totalweight") ne $ch[5]) {
      #free text can be float
      my $n = $q->param("totalweight");
      if (!DBI::looks_like_number($n)) { print_error("totalweight must be a number, %n"); }
      $set .= "totalweight = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("numtype2hits") && $q->param("numtype2hits") ne '' && $q->param("numtype2hits") ne $ch[6]) {
      #free text, should be integer
      my $n = $q->param("numtype2hits");
      if ($n =~ /\D/) { print_error("numtype2hits should be an integer, $n"); }
      $set .= "numtype2hits = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("totaltype2weight") && $q->param("totaltype2weight") ne '' && $q->param("totaltype2weight") ne $ch[7]) {
      #free text can be float
      my $n = $q->param("totaltype2weight");
      if (!DBI::looks_like_number($n)) { print_error("totaltype2weight must be a number, %n"); }
      $set .= "totaltype2weight = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("numpairs") && $q->param("numpairs") ne '' && $q->param("numpairs") ne $ch[8]) {
      #free text, should be integer
      my $n = $q->param("numpairs");
      if ($n =~ /\D/) { print_error("numpairs should be an integer, $n"); }
      $set .= "numpairs = ?, ";
      push(@bind, $n);
   }   
   if (defined $q->param("totalpairweight") && $q->param("totalpairweight") ne '' && $q->param("totalpairweight") ne $ch[9]) {
      #free text can be float
      my $n = $q->param("totalpairweight");
      if (!DBI::looks_like_number($n)) { print_error("totalpairweight must be a number, %n"); }
      $set .= "totalpairweight = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("aligndir") && $q->param("aligndir") ne '' && $q->param("aligndir") ne $ch[10]) {
      #free text
      my $n = $q->param("aligndir");
      $set .= "aligndir = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("alignfile") && $q->param("alignfile") ne '' && $q->param("alignfile") ne $ch[11]) {
      #free text
      my $n = $q->param("alignfile");
      $set .= "alignfile = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("idxfile") && $q->param("idxfile") ne '' && $q->param("idxfile") ne $ch[12]) {
      #free text
      my $n = $q->param("idxfile");
      $set .= "idxfile = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("collabalignid") && $q->param("collabalignid") ne '' && $q->param("collabalignid") ne $ch[13]) {
      #free text
      my $n = $q->param("collabalignid");
      $set .= "collabalignid = ?, ";
      push(@bind, $n);
   }
   if ($q->param("wiguploadstatus") && $q->param("wiguploadstatus") ne '' && $q->param("wiguploadstatus") ne $ch[14]) {
      #controlled vocab but not in db yet
      my $n = $q->param("wiguploadstatus");
      my %status = ("NOT UPLOADED"=>1, "UPLOADED"=>1, "IN PROGRESS"=>1, "FAILED"=>1);
      if (!$status{$n}) { print_error("Not a valid wiguploadstatus, $n"); }
      $set .= "wiguploadstatus = ?, ";
      push(@bind, $n);
   }
   #passed checks now update table
   push(@bind, $id);
   $set =~ s/, $//;
   #do as update because mysql will reset the auto_increment value every time
   if (scalar @bind > 1) { #only save if changes
      $dbh->do("update seqalignment set $set where id = ?", undef, @bind);
   } 
}
####

sub save_expt {
   my $id = shift;
   if ($id =~ /\D/) { print_error("Bad id $id"); }
   my @ch = $dbh->selectrow_array("select * from seqexpt where id = ?", undef, $id);
   if (!@ch) { print_error("ID $id does not exist"); }
   my @bind;
   my $set = ''; #set field = ? foreach changed value
   #only get changed fields, preselect name fields
   #composite of lab cond tar cell varchar(200)
   my @name = $dbh->selectrow_array("select core.lab.name, core.exptcondition.name, core.expttarget.name, core.cellline.name from seqexpt, core.exptcondition, core.expttarget, core.cellline, core.lab where seqexpt.id = ? AND seqexpt.exptcondition = core.exptcondition.id and seqexpt.expttarget = core.expttarget.id and seqexpt.cellline = core.cellline.id and seqexpt.lab = core.lab.id", undef, $id);
   #if ($q->param("name") && $q->param("name") ne '' && $q->param("name") ne $ch[1]) {
      #free text, 200 char limit
      #my $n = $q->param("name");
      #if (length $n > 200) { print_error("The name is too long, $n"); }
      #$set .= "name = ?, ";
      #push(@bind, $n);
   #}
   if ($q->param("replicate") && $q->param("replicate") ne '' && $q->param("replicate") ne $ch[2]) {
      #free text, 200 char limit
      my $n = $q->param("replicate");
      if (length $n > 200) { print_error("The replicate is too long, $n"); }
      $set .= "replicate = ?, ";
      push(@bind, $n);
   }
   if ($q->param("species") && $q->param("species") ne ' ') {
      my $n = $q->param("species");
      #switch to id for foreign key
      my @t = $dbh->selectrow_array("select id from core.species where name = ?", undef, $n);
      if (!@t) { print_error("Not a valid species $n"); }
      if ($t[0] ne $ch[3]) { #check row is id
         push(@bind, $t[0]);
         $set .= "species = ?, "
      }
   }
   if ($q->param("expttype") && $q->param("expttype") ne ' ') {
      my $n = $q->param("expttype");
      #switch to id for foreign key
      my @t = $dbh->selectrow_array("select id from core.expttype where name = ?", undef, $n);
      if (!@t) { print_error("Not a valid expttype $n"); }
      if ($t[0] ne $ch[4]) { #check row is id
         push(@bind, $t[0]);
         $set .= "expttype = ?, "
      }
   }
   if ($q->param("lab") && $q->param("lab") ne ' ') {
      my $n = $q->param("lab");
      #switch to id for foreign key
      my @t = $dbh->selectrow_array("select id from core.lab where name = ?", undef, $n);
      if (!@t) { print_error("Not a valid lab $n"); }
      if ($t[0] ne $ch[5]) { #check row is id
         push(@bind, $t[0]);
         $set .= "lab = ?, ";
         $name[0] = $n;
      }
   }
   if ($q->param("exptcondition") && $q->param("exptcondition") ne ' ') {
      my $n = $q->param("exptcondition");
      #switch to id for foreign key
      my @t = $dbh->selectrow_array("select id from core.exptcondition where name = ?", undef, $n);
      if (!@t) { print_error("Not a valid exptcondition $n"); }
      if ($t[0] ne $ch[6]) { #check row is id
         push(@bind, $t[0]);
         $set .= "exptcondition = ?, ";
         $name[1] = $n;
      }
   }
   if ($q->param("expttarget") && $q->param("expttarget") ne ' ') {
      my $n = $q->param("expttarget");
      #switch to id for foreign key
      my @t = $dbh->selectrow_array("select id from core.expttarget where name = ?", undef, $n);
      if (!@t) { print_error("Not a valid expttarget $n"); }
      if ($t[0] ne $ch[7]) { #check row is id
         push(@bind, $t[0]);
         $set .= "expttarget = ?, ";
         $name[2] = $n;
      }
   }
   if ($q->param("cellline") && $q->param("cellline") ne ' ') {
      my $n = $q->param("cellline");
      #switch to id for foreign key
      my @t = $dbh->selectrow_array("select id from core.cellline where name = ?", undef, $n);
      if (!@t) { print_error("Not a valid cellline $n"); }
      if ($t[0] ne $ch[8]) { #check row is id
         push(@bind, $t[0]);
         $set .= "cellline = ?, ";
         $name[3] = $n;
      }
   }
   if (@name) { 
      $set .= "name = ?, ";
      my $n = join(" ", @name);
      if (length $n > 200) { print_error("The name is too long, $n"); }
      push(@bind, $n);
   }
   if ($q->param("readtype") && $q->param("readtype") ne ' ') {
      my $n = $q->param("readtype");
      #switch to id for foreign key
      my @t = $dbh->selectrow_array("select id from core.readtype where name = ?", undef, $n);
      if (!@t) { print_error("Not a valid readtype $n"); }
      if ($t[0] ne $ch[9]) { #check row is id
         push(@bind, $t[0]);
         $set .= "readtype = ?, ";
      }
   }
   if (defined $q->param("readlength") && $q->param("readlength") ne '' && $q->param("readlength") ne $ch[10]) {
      #free text, should be integer
      my $n = $q->param("readlength");
      if ($n =~ /\D/) { print_error("readlength should be an integer, $n"); }
      $set .= "readlength = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("numreads") && $q->param("numreads") ne '' && $q->param("numreads") ne $ch[11]) {
      #free text, should be integer
      my $n = $q->param("numreads");
      if ($n =~ /\D/) { print_error("numreads should be an integer, $n"); }
      $set .= "numreads = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("collabid") && $q->param("collabid") ne '' && $q->param("collabid") ne $ch[12]) {
      #free text
      my $n = $q->param("collabid");
      if (length $n > 200) { print_error("collabid is too long $n"); }
      $set .= "collabid = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("publicsource") && $q->param("publicsource") ne '' && $q->param("publicsource") ne $ch[13]) {
      #free text
      my $n = $q->param("publicsource");
      if (length $n > 200) { print_error("publicsource is too long $n"); }
      $set .= "publicsource = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("publicdbid") && $q->param("publicdbid") ne '' && $q->param("publicdbid") ne $ch[14]) {
      #free text
      my $n = $q->param("publicdbid");
      if (length $n > 200) { print_error("publicdbid is too long $n"); }
      $set .= "publicdbid = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("fqfile") && $q->param("fqfile") ne '' && $q->param("fqfile") ne $ch[15]) {
      #free text
      my $n = $q->param("fqfile");
      if (length $n > 500) { print_error("fqfile is too long $n"); }
      $set .= "fqfile = ?, ";
      push(@bind, $n);
   }
   if (defined $q->param("exptnote") && $q->param("exptnote") ne '' && $q->param("exptnote") ne $ch[12]) {
      #free text, long text (~4G)
      my $n = $q->param("exptnote");
      $set .= "exptnote = ?, ";
      push(@bind, $n);
   }
   #passed checks now update table
   push(@bind, $id);
   $set =~ s/, $//;
   #do as update because mysql will reset the auto_increment value every time
   if (scalar @bind > 1) { #only save if changes
      $dbh->do("update seqexpt set $set where id = ?", undef, @bind);
   }
}
####

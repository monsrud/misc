#!/usr/bin/perl
#
# Script Name: sip_sync.pl
# Author:      Marshall Onsrud
# Email:       
# Description:
#
# sip_sync.pl exchanges SIP INVITE, OK, and BYE messages over the network.
# I wrote this when testing a device that needed to see SIP traffic going
# back and forth over a network in order to establish a VOIP call. I determined what 
# needed to be sent and received using Wireshark. I made my packets look the same.
# This example is from 2006-2008. 
#
#
use IO::Socket::INET;
use Getopt::Long;

$src_port   = undef;
$dest_port  = undef;
$src_addr   = undef;
$dest_addr  = undef;
$call_id    = undef;
$media_port = undef;

my $ret = GetOptions ('src_addr=s',        \$src_addr,
                      'src_portp=s',       \$src_port,
                      'dest_addr=s',       \$dest_addr,
                      'dest_port=s',       \$dest_port,
                      'media_port=s',      \$media_port,
                      'call_id=s',         \$call_id,
                      'message_type=s',    \$message_type
);

sub help {
    print "

    HELP

    sip_sync.pl exchanges SIP INVITE, OK, and BYE messages between hosts to create a sync session
    when there are no real SIP clients/servers involved.

    Steps are: 

        1) Create a fake INVITE request from the client to the server (no real sip server, just another host) 
        2) Create a fake OK response from the server back to the client
        3) Run other tests like IXIA Chariot over the RTP media ports you provided when you set the call up
        4) Send a fake BYE request from the client host to the server to close the call 

    -src_addr        : source ip address
    -src_port        : source port number (defaults to 5060)
    -dest_addr       : destination ip address
    -dest_port       : destination port number (defaults to 5060)
    -media_port      : media port number for the voip data
    -call_id         : a numeric value for the call id
    -message_type    : either of invite, bye, ok, or cancel.


    Example to setup/teardown a call between a client and a server:

    On the client side, issue an INVITE request to a server at dest_addr:
        sip_sync.pl -src_addr 192.168.1.2 -dest_addr 192.168.1.1 -message_type invite -media_port 10000

    On the server side, issue an OK back to the client:
        sip_sync.pl -src_addr 192.168.1.1 -dest_addr 192.168.1.2 -message_type ok -media_port 10000

    On the client side, issue a BYE message to a server at dest_addr:
        sip_sync.pl -src_addr 192.168.1.2 -dest_addr 192.168.1.1 -message_type bye 
    ";

    exit;
}

unless($src_addr)  { 
    print ("\n\n*** No source address specified\n\n"); 
    help();
}
unless($dest_addr) { 
    print ("\n\n*** No source address specified\n\n"); 
    help();
}

unless($message_type) { 
    print ("\n\n*** No message_type specified\n\n"); 
    help();
}

unless($src_port) {
    $src_port = 5060;
}

unless($dest_port) {
    $dest_port = 5060;
}

unless($call_id) {
    $call_id = 1234;
}


unless ($message_type eq 'ok' || $message_type eq 'bye' || $message_type eq 'invite' || $message_type eq 'cancel') {
    print ("\n\n*** Message type must be either invite, ok, bye_from_client or bye_from_server\n\n"); 
    help();
}

sub invite {
    $msg  = "INVITE sip:sip\@$dest_addr:$dest_port SIP/2.0\r\n";
    $msg .= "Via: SIP/2.0/UDP $src_addr:$src_port\r\n";
    $msg .= "From: sip <sip:sip\@$src_addr:$src_port>;tag=1\r\n";
    $msg .= "To: sip <sip:sip\@$dest_addr:$dest_port>\r\n";
    $msg .= "Call-ID: $call_id\@$src_addr\r\n";
    $msg .= "CSeq: 1 INVITE\r\n";
    $msg .= "Contact: sip:sip\@$src_addr:$src_port\r\n";
    $msg .= "Max-Forwards: 70\r\n";
    $msg .= "Subject: Performance Test\r\n";
    $msg .= "Content-Type: application/sdp\r\n";
    $msg .= "Content-Length: 255\r\n\r\n";
    $msg .= "v=0\r\n";
    $msg .= "o=user1 53655765 2353687637 IN IP4\r\n";
    $msg .= "s=-\r\n";
    $msg .= "c=IN IP4 $src_addr\r\n";
    $msg .= "t=0 0\r\n";
    $msg .= "m=audio $media_port RTP/AVP 18 8 0 101\r\n";
    $msg .= "a=rtpmap:18  G729/8000\r\n";
    $msg .= "a=rtpmap:8   PCMA/8000\r\n";
    $msg .= "a=rtpmap:0   PCMU/8000\r\n";
    $msg .= "a=rtpmap:101 telephony-event/8000\r\n";
    $msg .= "a=fmtp:101   0-15\r\n";
    return $msg;
}

sub bye {
    $msg  = "BYE sip:sip\@$dest_addr:$dest_port SIP/2.0\r\n";
    $msg .= "Via: SIP/2.0/UDP $src_addr:$src_port\r\n";
    $msg .= "From: sip <sip:sip\@$src_addr:$src_port>;tag=$call_id\r\n";
    $msg .= "To: sut <sip:sip\@$dest_addr:$dest_port>;tag=1\r\n";
    $msg .= "Call-ID: $call_id\@$src_addr\r\n"; 
    $msg .= "CSeq: 2 BYE\r\n";
    $msg .= "Contact: sip:sip\@$src_addr:$src_port\r\n";
    $msg .= "Max-Forwards: 70\r\n";
    $msg .= "Subject: Performance Test\r\n"; 
    $msg .= "Content-Length: 0\r\n\r\n";
    return $msg;
}

sub cancel {
    $msg  = "CANCEL sip:sip\@$dest_addr:$dest_port SIP/2.0\r\n";
    $msg .= "Via: SIP/2.0/UDP $src_addr:$src_port\r\n";
    $msg .= "From: sip <sip:sip\@$src_addr:$src_port>;tag=$call_id\r\n";
    $msg .= "To: sut <sip:sip\@$dest_addr:$dest_port>;tag=1\r\n";
    $msg .= "Call-ID: $call_id\@$src_addr\r\n";
    $msg .= "CSeq: 1 CANCEL\r\n";
    $msg .= "Content-Length: 0\r\n\r\n";
    return $msg;
}


sub ok {
    $msg  = "SIP/2.0 200 OK\r\n";
    $msg .= "Via: SIP/2.0/UDP $dest_addr:$dest_port\r\n";
    $msg .= "From: sip <sip:sip\@$dest_addr:$dest_port>;tag=1\r\n";
    $msg .= "To: sip <sip:sip\@$src_addr:$src_port>;tag=1\r\n";
    $msg .= "Call-ID: $call_id\@$dest_addr\r\n";
    $msg .= "CSeq: 1 INVITE\r\n";
    $msg .= "Contact: <sip:$src_addr:$src_port;transport=UDP>\r\n";
    $msg .= "Content-Type: application/sdp\r\n";
    $msg .= "Content-Length: 255\r\n\r\n";
    $msg .= "v=0\r\n";
    $msg .= "o=user1 53655765 2353687637 IN IP4 $src_addr\r\n";
    $msg .= "s=-\r\n";
    $msg .= "c=IN IP4 $src_addr\r\n";
    $msg .= "t=0 0\r\n";
    $msg .= "m=audio $media_port RTP/AVP 18 8 0 101\r\n";
    $msg .= "a=rtpmap:18  G729/8000\r\n";
    $msg .= "a=rtpmap:8   PCMA/8000\r\n";
    $msg .= "a=rtpmap:0   PCMU/8000\r\n";
    $msg .= "a=rtpmap:101 telephony-event/8000\r\n";
    $msg .= "a=fmtp:101   0-15\r\n";
    return $msg;
}

print "dest_port=$dest_port\n";
print "dest_addr=$dest_addr\n";
print "src_port=$src_port\n";
print "src_addr=$src_addr\n";

$sock=new IO::Socket::INET->new(PeerPort=>$dest_port,
                                PeerAddr=>$dest_addr,
                                LocalPort=>$src_port,
                                Local_Addr=>$src_addr, 
                                Proto=>17,
                                Type=>PF_INET,
                                 );

unless($sock) {
 print "Could not create socket\n";
}

$sock->send(&${message_type}());







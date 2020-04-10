#!/usr/bin/perl
# Simple DHCP client - send a LeaseQuery (by IP) and receive the response
# Needed to verify that dhcp would be blocked from going over a wireless network.
use strict;
use warnings;
use IO::Socket::INET;
use Net::DHCP::Packet;
use Net::DHCP::Constants;
use Getopt::Long;

my $server;
my $client;
my $client_mac = '00:00:00:00:00:AA';
my $message;

my $ret = GetOptions ('server=s'   , \$server, 
                      'client=s',      \$client,
                      'help',      , sub { help(); });


sub help {
    print "Send spoof DHCP ack/nak/offer messages from a host over the airlink to make sure they are filtered\n\n\n"; 
    print "-server : this is address of the server we are claiming to be\n"; 
    print "-client : this is address of the client we are sending the ack/nak/offer to\n"; 
    exit;
}

unless(defined($server) && defined($client)) {
    help();
}

$| = 1;

# create a socket
my $sock = IO::Socket::INET->new(Proto => 'udp',
                                Broadcast => 1,
                                PeerPort => '68',
                                LocalPort => '67',
                                LocalAddr => $server,
                                PeerAddr => $client)
              or die "socket: $@";     # yes, it uses $@ here

# send a DHCP ACK
$message = new Net::DHCP::Packet(
                                   Comment => 'spoof ack',
                                   Op => BOOTREPLY(),
                                   Hops => 0,
                                   Xid => 0x12345678,
                                   Flags => 0,
                                   Ciaddr => '0.0.0.0',
                                   Yiaddr => $client,
                                   Siaddr => $server,
                                   Chaddr => $client_mac,
                                   DHO_DHCP_MESSAGE_TYPE() => DHCPACK(),
                                 );

# send request
$sock->send($message->serialize()) or die "Error sending dhcp ack: $!\n";


# Send a DHCP NAK 
$message = new Net::DHCP::Packet(
                                  Comment => 'spoof nak',
                                  Op => BOOTREPLY(),
                                  Hops => 0,
                                  Xid => 0x12345678,
                                  Flags => 0,
                                  Ciaddr => '0.0.0.0',
                                  Yiaddr => '0.0.0.0',
                                  Siaddr => $server,
                                  Chaddr => $client_mac,
                                  DHO_DHCP_MESSAGE_TYPE() => DHCPNAK(),
                                  DHO_DHCP_MESSAGE(), "Bad request...",
                                  );

$sock->send($message->serialize()) or die "Error sending dhcp nak: $!\n";

$message = new Net::DHCP::Packet(
                                 Comment => 'spoof offer',
                                 Op => BOOTREPLY(),
                                 Hops => 0,
                                 Xid => 0x12345678,
                                 Flags => 0,
                                 Ciaddr => '0.0.0.0',
                                 Yiaddr => '0.0.0.0',
                                 Siaddr => '169.254.0.1',
                                 Chaddr => $client_mac,
                                 DHO_DHCP_MESSAGE_TYPE() => DHCPOFFER(),
                                );

$sock->send($message->serialize()) or die "Error sending dhcp offer: $!\n";

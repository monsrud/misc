#!/usr/bin/perl
use HTTP::Daemon;
use HTTP::Status;
use HTTP::Response;
use HTTP::Headers;

# When I was working for a video content delivery company, I wrote this to
# collect data about the quality, rate, packets sent,  and packets recieved 
# while streaming an online video with Windows Media Player.  The data was 
# output to a file. Later, the file was parsed and graphed. The same video
# would then be watched at different available bandwidths like what a user
# might have in their home. The bandwith control was done with BSD's Dummynet. 

$| = 1;
#
# tool to spoof a server running WMSIISLOG.DLL and get log posts from windows media player
#
#
# create an asx file that points to the content you want
# make sure the logurl is http://127.0.0.1:8003
# point your wmp client at the asx file 
#
# <Asx Version = "3.0" >
# <LOGURL href="http://127.0.0.1:8003" />
# <Entry>
# <Title> "Marshall's Test Content" </Title>
# <REF href="mms://local.swarmcast.net:8001/protected/content/live?streambase=http://192.168.100.34:8080/tester/test.wmv" /> 
# </Entry>
# </Asx>
#

#
# view the following for field descriptions of the windows media player log fields
#
# http://msdn.microsoft.com/en-us/library/ms741602(VS.85).aspx
#

@fields = ('c-ip','date','time','c-dns','cs-uri-stem','c-starttime','x-duration','c-rate','c-status',
           'c-playerid','c-playerversion','c-playerlanguage','cs(User-Agent)','cs(Referer)',
           'c-hostexe','c-hostexever','c-os','c-osversion','c-cpu','filelength','filesize',
           'avgbandwidth','protocol','transport','audiocodec','videocodec','channelURL','sc-bytes',
           'c-bytes','s-pkts-sent','c-pkts-received','c-pkts-lost-client','c-pkts-lost-net',
           'c-pkts-lost-cont-net','c-resendreqs','c-pkts-recovered-ECC','c-pkts-recovered-resent',
           'c-buffercount','c-totalbuffertime','c-quality','s-ip','s-dns','s-totalclients',
           's-cpu-util','s-content-path','cs-user-name','s-session-id'
           );


$d = new HTTP::Daemon LocalPort=>8003;
while (my $c = $d->accept) {
    while (my $r = $c->get_request) {
        if ($r->method eq 'GET') {
            $header   = HTTP::Headers->new( Content_Type => 'text/html'); 
            $content = "<head><title>WMS ISAPI LOG Dll/9.01.01.3841</title></head>\n";
            $content .= "<body><h1>WMS ISAPI Log Dll/9.01.01.3841</h1></body>\n";
            $response = HTTP::Response->new( 200, 'OK', $header, $content );
            $c->send_response($response);
        }

        if ($r->method eq 'POST') {
            print "$r->{'_content'}\n";
            $r->{'_content'}  =~ s/[ ]+/ /g; 
            $r->{'_content'}  =~ s/\t//g; 
            $r->{'_content'}  =~ s/MX_STATS_LogLine: //; 
            @parts = split(/ /,$r->{'_content'});
            $i=0; 
            foreach $part (@parts) {
                printf("%-25.25s : %s\n", $fields[$i], $part);
                $i++;
            }
        }
    }
    $c->close;
    undef($c);
}

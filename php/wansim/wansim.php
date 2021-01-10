<?php
header("Cache-Control: no-cache, must-revalidate"); // HTTP/1.1
header("Expires: Sat, 26 Jul 1997 05:00:00 GMT"); // Date in the past


//// I built a simple traffic tool to simulate packet loss, latency/delay, or packet corruption
// using bridgectl and Linux's tc (Traffic Control) command. I used this tool as a convenience
// for being able to throttle traffic to/from the device under test.


// The user the web server runs as must be in /etc/sudoers as follows:
// www-data        ALL=NOPASSWD: /sbin/tc, /usr/sbin/brctl, /sbin/ifconfig
// This allows the above commands to be executed by the web server without
// requiring a password
// change the names of the interfaces by creating a new version of the 
// /etc/udev/rules.d/70-persistent-net.rules file... call it
// 71-persistent-net.rules and create friendly interface names.


if (file_exists("/sbin/ethtool")) {
    $ethtool = "/sbin/ethtool";
} else {
    echo "ethtool not found. Is package installed?";
    exit;
}

$perms = substr(sprintf('%o',fileperms("$ethtool")),-4);
if ($perms != 6755) {
    echo "Permissions must be 6755 for $ethtool";
    exit;
}

$self = $_SERVER['PHP_SELF'];

if (isset($_GET['interface']) && isset($_GET['nstate']) && isset($_GET['nparam'])) {
    $state = $_GET['nstate'];
    $param = $_GET['nparam'];
    $interface = $_GET['interface'];
    $cmd = "$ethtool -K $interface $param $state 2>&1";
    $output = array();

echo "command = $cmd\n";
    exec("$cmd",$output);
    $errmsg = $output[0];
}

echo "<html><title>WanSim</title><body bgcolor=#FFFFCC>";

//
// If the form was submitted, make requested changes
//
if (isset($_GET['submit'])) {
    $action = $_GET['action'];
    $range = $_GET['range'];
    $delay = $_GET['delay'];
    $limit = $_GET['limit'];
    $loss = $_GET['loss'];
    $duplicate = $_GET['duplicate'];
    $corrupt = $_GET['corrupt'];
    $interface = $_GET['interface'];

    if ($action == 'change') {
        mod($interface,$action,$limit,$delay,$range,$loss,$duplicate,$corrupt);
    }

    if ($action == 'del') {
        $cmd.= "/usr/bin/sudo /sbin/tc qdisc " . $action . " dev $interface root netem";
        exec("$cmd",$output);
        echo "executed command : $cmd<br><br>";
        sleep(1);
    }

    if ($action == 'add') {
        mod($interface,$action,$limit,$delay,$range,$loss,$duplicate,$corrupt);
    }

    if ($action == 'changebridgeifstate') {
        if (preg_match('/^[A-z0-9]+$/',$_GET['bridgeiface'])  && preg_match('/^[a-z]+$/',$_GET['state']) ) {
            exec("sudo /sbin/ifconfig " . $_GET['bridgeiface']  . " " . $_GET['state']);
        }
    }

    if ($action == 'deletebridge') {
        if (preg_match('/^[A-z0-9]+$/',$_GET['bridgeiface'])) {
            exec("sudo ifconfig "  . $_GET['bridgeiface'] . " down");
            exec("sudo brctl delbr "  . $_GET['bridgeiface']);
        }

    }

    if ($action == 'createbridge') {

        if (preg_match('/^[A-z0-9]+$/',$_GET['bridgename'])) {
            if (preg_match('/^[A-z0-9]+$/',$_GET['int1']) && preg_match('/^[A-z0-9]+$/',$_GET['int2'])) {

                exec("sudo brctl addbr "  . $_GET['bridgename']);
                exec("sudo brctl addif "  . $_GET['bridgename'] . " " . $_GET['int1']);
                exec("sudo brctl addif "  . $_GET['bridgename'] . " " . $_GET['int2']);
                exec("sudo ifconfig "  . $_GET['bridgename'] . " up");


            }
        }
    }

}

function mod ($interface,$action,$limit,$delay,$range,$loss,$duplicate,$corrupt) {
        $cmd.= "/usr/bin/sudo /sbin/tc qdisc " . $action . " dev $interface root netem ";
        if (isset($limit) && $limit != '') {
            $cmd .= "limit $limit ";
        }

        if (isset($delay) && $delay != '') {
            $cmd .= "delay ${delay}ms ";
        }

        if (isset($range) && $range != '') {
            $cmd .= " ${range}ms ";
        }

        if (isset($loss) && $loss != '') {
            $cmd .= " loss ${loss}% ";
        }

        if (isset($duplicate) && $duplicate != '') {
            $cmd .= " duplicate ${duplicate}% ";
        }

        if (isset($corrupt) && $corrupt != '') {
            $cmd .= " corrupt ${corrupt}% ";
        }

        exec("$cmd",$output);
        echo "executed command : $cmd<br><br>";
        sleep(1);
}

echo "<h3><img src='img.png' align=middle> WanSim (execute tc commands via web form)</h3>";

echo "<table border=1 cellpadding=5 cellspacing=0 bgcolor=#CCCCCC>";
echo "<tr><td colspan=2 align=center>";


//
// Display the table/form
//


// get all the interfaces
exec('/sbin/tc qdisc show',$output);
$interfaces = array();
foreach ($output as $line) {
    preg_match('/dev ([A-z0-9]+) /',$line,$match);
    array_push($interfaces,$match[1]);

}

echo "<table border cellpadding=5 cellspacing=0 bgcolor=#FFFFFF>";
echo "<tr><td colspan=11 align=center bgcolor=#6699CC><font size=+1><B>Alter Traffic Flow</B></font> </td></tr>";
echo "<tr><td><b>Interface</b></td><td><b>Limit</b></td><td><b>Delay ms</b></td><td><b>Range ms</b></td><td><b>Loss %</b></td><td><b>Duplicate %</b></td><td><b>Corrupt %</b></td><td><b>Output from tc</b></td><td><b>Action</b></td><td></td></tr>";



foreach ($interfaces as $interface) {

   if ($interface == 'eth0' || $interface == 'eth1') { continue; }

   $output = array();
   $limit='';
   $delay='';
   $range='';
   $loss='0';
   $duplicate='0';
   $corrupt='0';

   exec("/sbin/tc qdisc show dev $interface",$output);

   if (preg_match('/limit ([0-9]+)/',$output[0],$match)) {
      $limit = $match[1];
   }

   if (preg_match('/delay ([0-9]+)\.0ms/',$output[0],$match)) {
      $delay = $match[1];
   }

   if (preg_match('/loss ([0-9\.]+)%/',$output[0],$match)) {
      $loss = $match[1];
   }

   if (preg_match('/duplicate ([0-9\.]+)%/',$output[0],$match)) {
      $duplicate = $match[1];
   }

   if (preg_match('/corrupt ([0-9\.]+)%/',$output[0],$match)) {
      $corrupt = $match[1];
   }

   if (preg_match('/  ([0-9]+)\.0ms$/',$output[0],$match)) {
      $range = $match[1];
   }

   echo "<form action=\"" . $_SERVER['PHP_SELF'] . "\">";
   echo "<tr><td><b>$interface</b></td><td><input type='text' name='limit' value='$limit' size='7'></td>";
   echo "<td><input type='text' name='delay' value='$delay' size='7'></td>";
   echo "<td><input type='text' name='range' value='$range' size='7'></td>";
   echo "<td><input type='text' name='loss' value='$loss' size='7'></td>";
   echo "<td><input type='text' name='duplicate' value='$duplicate' size='7'></td>";
   echo "<td><input type='text' name='corrupt' value='$corrupt' size='7'></td>";

   echo "<td>$output[0]</td>";

   // determine whether there is already a tc entry for each interface and set the form's default to "add" or "change" the entry  
   $default = 'change';
   if (preg_match('/^qdisc mq 0: root$/',$output[0],$match)) {
       echo "<td><select name=action><option selected value='add'>add</option></select></td>";
   } else {
       echo "<td><select name=action><option selected value='change'>change</option><option value='del'>delete</option></select></td>";
   }

   echo "<td><input name=submit type=submit value=submit></td></tr>";
   echo "<input type=hidden name=interface value=$interface>";
   echo "</form>";


}

echo "</table>";
echo "</td></tr>";
echo "<tr><td align=center bgcolor=#CCCCCC>";

    // display current bridge status 

    exec('sudo brctl show',$output);
    echo "<table border=1 cellpadding=5 cellspacing=0 bgcolor=#FFFFFF>";
    echo "<tr><td colspan=5 align=center bgcolor=#6699CC><font size=+1><b>Bridge Status</b></font></td></tr>";
    echo "<tr><td><b>Bridge Iface</b></td><td><b>Phys Iface1</b></td><td><b>Phys Iface2</b></td><td><b>State</b></td><td><b>Delete</b></td></tr>";
    foreach ($output as $line) {
        if (preg_match('/^([A-z0-9]+)\t/',$line,$match)) {
            $bridge = $match[1];

 
            exec("/sbin/ifconfig $bridge | grep UP",$opt,$ret);
            if ($ret == 0) { 
                $state_txt = "<font color=green>Up</font>";
                $change_state = 'down';
                $arr = '&darr;';
            } else {
                $state_txt = "<font color=red>Down</font>";
                $change_state = 'up';
                $arr = '&uarr;';
            }
         

        }

        if (preg_match('/[\t]{7}/',$line)) {
            $interface2 = preg_match('/[\t]{7}([A-z0-9]+)$/',$line,$match);
            $interface2 = $match[1];
            $change = $_SERVER['PHP_SELF'];
            $change .= "?action=changebridgeifstate&amp;state=$change_state&amp;bridgeiface=$bridge&amp;submit=true";

            $delete = $_SERVER['PHP_SELF'];
            $delete .= "?action=deletebridge&amp;bridgeiface=$bridge&amp;submit=true";

            echo "<tr><td>$bridge</td><td>$interface1</td><td>$interface2</td><td>$state_txt <a href='$change'><b>$arr</b></a></td><td><a href='$delete'>Delete</a></td></tr>";
            continue; // get out of here
        }

        $interface1 = preg_match('/([A-z0-9]+)$/',$line,$match);
        $interface1 = $match[1];

    }
    echo "</table>";


echo "<br>";

    // add a new bridge interface 
    $output = array();
    $bridges = array();
    $interfaces = array();
    exec('sudo brctl show',$output);

    foreach ($output as $line) {
        if (preg_match('/^([A-z0-9]+)\t/',$line,$match)) {
            $bridge = $match[1];
            array_push($bridges,$bridge);
        }

        $interface = preg_match('/([A-z0-9]+)$/',$line,$match);
        $interface = $match[1];
        array_push($interfaces,$interface);
    }

    $dont_use = array('lo','eth0','eth1');
    $available_interfaces = array();
    exec('sudo ifconfig | grep "Link encap:Ethernet"',$output);
    foreach ($output as $line) {
        if (preg_match('/([0-9A-z]+)/',$line,$match)) {
            $interface = $match[1];
            $interface = trim($interface);

            if ($interface == 'bridge') { continue; }

            $m1 =  preg_grep("/^$interface$/",$interfaces);
            $m2 =  preg_grep("/^$interface$/",$bridges);
            $m3 =  preg_grep("/^$interface$/",$dont_use);

            if ( count($m1) + count($m2) + count($m3) == 0 ) {
               array_push($available_interfaces,$interface);
            }

        } else {
           echo "did not match: $line<br>";
        }

    }

    if (count($available_interfaces) >=2) {

         echo "<form action='" . $_SERVER['PHP_SELF'] . "'>";
         echo "<table border=1 cellpadding=5 cellspacing=0 bgcolor=#FFFFFF>";
         echo "<tr><td align=center colspan=4 bgcolor=#6699CC><font size=+1><b>Create Bridge</b></font></td></tr>";
         echo "<tr><td><b>Bridge Name</b></td><td><b>Int 1</b></td><td><b>Int 2</b></td><td></td></tr>";
         echo "<tr><td><input type=text name=bridgename></td>";
         echo "<td><select name=int1>";
         foreach ($available_interfaces as $interface) {
             echo "<option value='$interface'>$interface</option>";
         } 
         echo "</select></td>";

         echo "<td><select name=int2>";
         foreach (array_reverse($available_interfaces) as $interface) {
             echo "<option value='$interface'>$interface</option>";
         } 
         echo "</select></td><td><input type=hidden name=action value=createbridge><input type=submit name=submit value=Add></td></tr>";

         echo "</form>";
         echo "</table>";

    } else {
        echo "Two interfaces  must be present to create another bridge.<br>";
    }

echo "</td><td align=center bgcolor=#CCCCCC>";

    // network stats
    $output = array();
    exec('cat /proc/net/dev',$output);
    echo "<table cellpadding=5 cellspacing=0 border=1 bgcolor=#FFFFFF>";
    echo "<tr><td colspan=5 align=center bgcolor=#6699CC><font size=+1><b>Network Statistics</b></font></td></tr>";
    echo "<tr><td><b>Device</b></td><td><b>State</b></td><td><b>Received KiB</b></td><td><b>Sent KiB</b></td><td><b>Err/Drop</b></td></tr>";
    $dont_use = array('lo','eth0','eth1');
    foreach ($output as $line) {
       if (preg_match('/:/',$line)) {
            list($dev_name, $stats_list) = preg_split('/:/', $line, 2);
            $dev_name = trim($dev_name);
            if( preg_grep("/^$dev_name$/",$dont_use)) {
                continue;
            }
//            exec('sudo ifconfig $dev_name | grep "UP"',$output2);
//            if (preg_grep('/UP/',$output2)) {
//               echo "$dev_name is up<br>\n";
//            }

            exec("sudo /sbin/ifconfig $dev_name | grep UP",$opt,$ret);
            if ($ret == 0) { 
                $state_txt = "<font color=green>Up</font>";
                $change_state = 'down';
                $arr = '&darr;';
            } else {
                $state_txt = "<font color=red>Down</font>";
                $change_state = 'up';
                $arr = '&uarr;';
            }


            $stats = preg_split('/\s+/', trim($stats_list));
            $dev_name = trim($dev_name);
            $rx_bytes = sprintf("%0.2f",trim($stats[0]) / 1024);
            $tx_bytes = sprintf("%0.2f",trim($stats[8]) /1024);


            $errors = trim($stats[2]) + trim($stats[10]);
            $dropped = trim($stats[3]) + trim($stats[11]);

            $change = $_SERVER['PHP_SELF'];
            $change .= "?action=changebridgeifstate&amp;state=$change_state&amp;bridgeiface=$dev_name&amp;submit=true";

            echo "<tr><td><b>$dev_name</b></td><td>$state_txt <a href='$change'><b>$arr</b></a></td><td>$rx_bytes</td><td>$tx_bytes</td><td>$errors/$dropped</td></tr>";

       }
    }
    echo "</table>";


echo "</td></tr></table>";
echo "<br><br>";


/*
//
// THE next section is about editing tcp offload parameters with ethtool
//
*/

// get all the interfaces
$output = array();
exec('/sbin/tc qdisc show',$output);
$interfaces = array();
foreach ($output as $line) {
    preg_match('/dev ([A-z0-9]+) /',$line,$match);
    array_push($interfaces,$match[1]);
}

$numcols = 4;
echo "<table border cellpadding=5 cellspacing=0 bgcolor=#FFFFFF>";
echo "<tr><td colspan=$numcols align=center bgcolor=#6699CC><font size=+1><B>Edit NIC Offload Parameters</B></font> </td></tr>";
$cnt=0;
$tot=0;
foreach ($interfaces as $interface) {

    if ($cnt == 0) { echo "<tr>"; }
    echo "<td>";
    $cmd = "$ethtool -k $interface";
    $output = array();
    exec("$cmd",$output);
    echo "<table border cellpadding=5 cellspacing=0 bgcolor=#FFFFFF>";
    foreach ($output as $line) {
       if ( preg_match("/Offload/",$line)) {
           //echo "line=$line\n";
           echo "<tr><td colspan=3 align=center bgcolor=#6699CC><font size=+1><B>Interface: $interface</B></font> </td></tr>";
           echo "<tr><td>Offload parameters</td><td>State</td><td>Change</td></tr>";
       } else {
           $parts = preg_split("/: /",$line);
           $parameter = $parts[0];
           $state = $parts[1];
           if ($state == "off") { $nstate = "on"; }
           if ($state == "on") { $nstate = "off"; }
           if ($parameter == "rx-checksumming") { $nparam = "rx"; }
           if ($parameter == "tx-checksumming") { $nparam = "tx"; }
           if ($parameter == "scatter-gather") { $nparam = "sg"; }
           if ($parameter == "tcp-segmentation-offload") { $nparam = "tso";  }
           if ($parameter == "udp-fragmentation-offload") { $nparam = "ufo"; }
           if ($parameter == "generic-segmentation-offload") { $nparam = "gso"; }
           if ($parameter == "generic-receive-offload") { $nparam = "gro"; }
           if ($parameter == "large-receive-offload") { $nparam = "lro"; }
           if ($parameter == "ntuple-filters") { $nparam = "ntuple"; }
           if ($parameter == "receive-hashing") { $nparam="rxhash"; }
           echo "<tr><td>$parameter</td><td>$state</td><td><a href='$self?interface=$interface&amp;nstate=$nstate&amp;nparam=$nparam'>[change]</a></td></tr>";
       }

    }
    echo "</table>";
    echo "</td>";
    $cnt++;
    $tot++;
    if ($cnt == $numcols) { echo "</tr>"; $cnt = 0;}
    if (isset($errmsg)) { echo "<font color=red>$errmsg</font>";}
}
if (count($interfaces) % $numcols) { echo "</tr>"; }
echo "</table>";




echo "<br><br>";
echo "<a target=new href='http://www.linuxfoundation.org/collaborate/workgroups/networking/netem'>netem guide</a></body></html>";


?>

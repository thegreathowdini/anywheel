# powershell

Here are four commands intended to be run on windows powershell. If you don't already have a valid token, the [first two commands](#tokengen) generate one. With a valid token, the [third command](#daily) performs check-in and trip-sharing for your account, and the fourth buys a 7-day pass for 200 points.

### how to start powershell
Press Windows+X. In the menu that appears, choose 'Windows Powershell'.

<a name="tokengen"/>

### token generation
If you have a valid token, skip to the [third command](#daily). Otherwise, you'll need the phone number associated with your anywheel account. Change the first line of the below code block to include your phone number, then copy-paste the entire code block into powershell.
```
$mobileNumber="91234567"

$d='{"type":1,"cc":"65","mobile":"'+$mobileNumber+'"}';$h=@{'X-Atayun-Os-Version'='15.5';'X-Atayun-Os'='0';'Content-Type'='application/json';'Authorization'='Basic YW55d2hlZWw6TXNId3lPMDB5S0RhMzlCeU0=';'X-Atayun-Version'='2.2.3';'X-Atayun-Api-Version'='10';'Accept'='*/*';'X-Atayun-Network'='0';'Accept-Language'='en-SG;q=1';'Accept-Encoding'='gzip; deflate';'X-Atayun-Screen'='750x1334';'X-Atayun-Brand'='iPhone SE (2nd generation)';'User-Agent'='Anywheel/2.2.3 (iPhone; iOS 15.5; Scale/2.00)';'X-Atayun-Versioncode'='267'};$r=$(convertfrom-json (iwr https://appgw.justscoot.com/noAuth/login/captcha -usebasicparsing -headers $h -method POST -body $d).content);if ($r.msg -eq 'Your verification code has been sent.'){echo 'OTP sent'} elseif ($r.msg -eq 'Sms verification failed, please try again in 10 Minutes.'){echo 'OTP requested too recently'} elseif ($r.msg -eq 'Incorrect format of mobile phone number.'){echo 'number in incorrect format'} else {echo 'error'}
```
If the mobile number you provided was right, the console will print 'OTP sent', and an OTP will be sent to that number. If you haven't received the OTP after about a minute, try the above command again. When you have the OTP value, change the first line of the below code block to include it, then copy-paste the entire code block into powershell.
```
$code="0000"

$d='{"code":"'+$code+'","cc":"65","mobile":"'+$mobileNumber+'","tt":'+$([math]::floor($(date -uformat %s))*1000)+'}';$r=$(convertfrom-json (iwr https://appgw.justscoot.com/noAuth/login -usebasicparsing -headers $h -method POST -body $d).content);if ($r.code -eq 0){echo 'OTP correct. token value: '$($r.data.token)} elseif ($r.code -eq 1000){echo 'incorrect OTP code'} else {echo 'error'}
```
If the OTP value you provided was right, the console will print the value of a valid token.

<a name="daily"/>

### daily tasks
If you have the value of a valid token, the below code block does your daily tasks of checking-in and sharing a recent trip (if you have one). Change the first line of the below code block to include the value of your token, then copy-paste the entire code block into powershell.
```
$token="1_999999_TOKEN-TOKENTOKEN-TOKEN"

$h=@{'X-Atayun-Os-Version'='15.5';'X-Atayun-Os'='0';'Content-Type'='application/json';'Authorization'='Basic YW55d2hlZWw6TXNId3lPMDB5S0RhMzlCeU0=';'X-Atayun-Version'='2.2.3';'X-Atayun-Api-Version'='10';'Accept'='*/*';'X-Atayun-Network'='0';'Accept-Language'='en-SG;q=1';'Accept-Encoding'='gzip; deflate';'X-Atayun-Screen'='750x1334';'X-Atayun-Brand'='iPhone SE (2nd generation)';'User-Agent'='Anywheel/2.2.3 (iPhone; iOS 15.5; Scale/2.00)';'X-Atayun-Versioncode'='267';'X-Atayun-Token'=$token};$r=$(convertfrom-json (iwr https://appgw.justscoot.com/event/challenges/points/today -usebasicparsing -headers $h).content);if ($r.data.checkInTimes -eq 1){echo "already checked in today"} else {$a=$(iwr https://appgw.justscoot.com/event/challenges/checkIn -usebasicparsing -headers $h);echo "checked in"};if ($r.data.shareTripTimes -eq 1){echo "already shared trip today"} else {$s=$(convertfrom-json (iwr "https://appgw.justscoot.com/lock/trip/list?pageNum=1" -usebasicparsing -headers $h).content);$shared=0;foreach ($t in $s.data){if ($($([math]::floor($(date -uformat %s))*1000)-$t.gmtCreate) -le 72*3600*1000){$d='{"tripId":"'+$t.id+'"}';$a=$(iwr https://appgw.justscoot.com/lock/trip/share/complete -usebasicparsing -headers $h -method POST -body $d);$r=$(convertfrom-json (iwr https://appgw.justscoot.com/event/challenges/points/today -usebasicparsing -headers $h).content);if ($r.data.shareTripTimes -eq 1){$shared=1;break;}}};if ($shared -eq 1){echo "shared trip"} else {echo "no viable trips to share"}};$r=$(convertfrom-json (iwr https://appgw.justscoot.com/event/challenges/points -usebasicparsing -headers $h).content);if ($r.code -eq 0){echo "point total: "$($r.data.point)} else {echo "token error"}
```
The console will report the results of the daily tasks and finish by showing your current point total. For as long as the token you have is valid, you can do the daily tasks just by running the same code block.

<a name="pass"/>

### 7-day pass
After running the above code block, you can buy a 7-day pass for 200 points by running the below code block. It'll work only if you have at least 200 points.
```
$r=$(convertfrom-json (iwr https://appgw.justscoot.com/event/challenges/points/redeem -usebasicparsing -method POST -headers $h -body '{"reward":"4"}').content);if ($r.code -eq 0){echo "success"} elseif($r.code -eq 1){echo "insufficient points"} else {echo "token error"}
```


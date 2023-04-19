# anywheel

In this repo are scripts for exploiting vulnerabilities found in Anywheel < 2.4.1.

### Vulnerabilities
Anywheel < 2.4.1 contained the following vulnerabilities that could be exploited in conjunction to allow users to use the app more cheaply or conveniently.

1. **Lack of SSL certificate pinning** [vulnerable as of v2.4.1]. The client app does not verify the SSL certificate of the remote endpoint, allowing users to insert a proxy in an MITM position and examine app traffic. This allowed users to retrieve their authentication tokens and probe the server to discover further vulnerabilities.

2. **Unencrypted app traffic** [partially patched in v2.3.7, fully patched in v2.4.1]. Traffic sent from the client app was unencrypted, allowing users to examine and tamper with app data. In Anywheel < 2.3.7, login traffic was unencrypted, allowing users to request OTPs and, given a valid OTP, generate authentication tokens without using the app. In v2.3.7, login traffic was encrypted, but traffic from other parts of the app were still in the clear.

3. **Logic flaw** [patched in v2.2.4]. Anywheel <= 2.2.3 allowed users to redeem 7-day passes for 200 points. The points system allowed users to attain 40 points a day for as long as they are on a pass. Users with 200 points can thus extend their pass validity indefinitely without cost. In v2.2.4, 7-day passes can no longer be redeemed.

4. **Excessive trust in client-side data** [patched in v2.4.1]. The server read the client app version off the 'X-Atayun-Version' header and behaved accordingly, allowing users to recover functionality from outdated versions of the app. By setting the value of the 'X-Atayun-Version' header to '2.2.3', users could redeem 7-day passes for 200 points and exploit the previous vulnerability.

5. **Insecure direct object reference** [patched in v2.4.1]. By modifying the tripId parameter in requests to /lock/trip/path, users could see information about trips made by other users.


### Exploit scripts
Anywheel.py is the main one. Run the script without arguments to see the help message, which enumerates the script's functions

![help message](img/help-msg.png)

Some exploits have also been implemented in [notebook form](anywheel.ipynb) with [step-by-step instructions](ipynb-instructions.pdf). For windows users, a limited number of script functions have been written as commands you can run from [Powershell](powershell.md).

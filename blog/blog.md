# SecurityCamera
## A bit about this project
I have a security camera which uses the [CamHipro app](https://camhi.pro/) as an interface on mobile phones. I get alerts when someone walks into frame, but those alerts have no images. The camera can record to the internal SD card as standard, but I want to be able to see what is going on without having to extract the SD card every time. CamHipro supports sending captures (images) to email or FTP, and can send recordings to FTP too... but I don't have an FTP server.

Let's use AWS to allow CamHipro to send images and links to records to me by email so I can see what is going on at my house even when I'm not actively looking at the live feed on my phone.
## Setting up your AWS account
1. Create an account on AWS. 
2. Add multi-factor authentication with a one-time password application like [Authy](https://authy.com/). Make sure whatever application you opt for, you have the ability to restore your keys from a new device if necessary -- the last thing you want is to setup 2FA for everything only to be locked out when you lose your phone.
3. Secure your root user: https://cloudaffaire.com/secure-aws-root-account/
4. Set up billing alerts so you know when your usage exceeds what is offered by the AWS free tier: https://medium.com/@rahulvenati/day-3-aws-free-tier-and-creating-a-billing-alarm-fc885083fe5d

## Installing packages on Windows
This guide is for a Windows 10 user. You can find many guides on how to install Terraform and AWS Vault for Linux or Mac with a little Googling.
1. Using a Powershell terminal running with admin privileges, [install Chocolatey](https://chocolatey.org/install), a package manager for Windows like Homebrew. 
2. Install [Terraform](https://community.chocolatey.org/packages/terraform) to manage our infrastructure: `choco install terraform` 
3. Install [AWS Vault](https://community.chocolatey.org/packages/aws-vault) to manage our AWS credentials: `choco install aws-vault`
4. Install the [AWS CLI](https://community.chocolatey.org/packages/awscli) so we can interact with AWS from the command line: `choco install awscli`
5. Install [Git](https://community.chocolatey.org/packages/git) to version control your project folder: `choco install git`
6. Install the GitHub CLI so we can easily interact with GitHub from the terminal: `choco install gh`
7. Restart your Powershell session when done.

## Setup the GitHub CLI
1. If you don't have a GitHub account, go create one before moving on.
2. Authenticate with GitHub. Enter `gh auth login` and follow the instructions. If you are unsure, you want to log into `Github.com` and you probably want to use `HTTPS` instead of `SSH`. Follow the remaining steps given to consent to the CLI tool having access to your GitHub account. 

## Setup your project folder
1. Create a folder for your project, I put mine in `C:\Users\james\Projects\SecurityCamera`
2. Initialize your Git repository: `git init`
3. Create a new file in your project folder, this is where we will add our Terraform config later:`New-Item -Type File main.tf` (in Powershell, weird syntax if you are used to Unix, I know!)
4. Let's commit this file so we can setup a remote repo in GitHub . First, stage `main.tf` using `git add .\main.tf`, then commit the file with a message using `git commit -m "Initial commit"`. If this is your first time using Git on your computer, you will be asked to enter your name and email. Just follow the details given to you in the config and then rerun the `commit` command.
5. Let's push this repo to GitHub. Enter `gh repo create` and then select `Push an existing local repository to GitHub`. If you are in the project folder, just use `.` as the path to the local repo, or else enter your project directory's path. Enter a name and description, then setup a remote repo and push your existing commits to it. Now your project will be backed up to GitHub so you can pull your code to other machines easily.
### Warning about pushing to GitHub!
Never **ever** add anything to your repo that you would consider security credentials: this is especially true of your AWS credentials, secret keys, etc. 

## Setup an AWS user for your project
![Creating a new AWS user for your project](https://github.com/jamesinjapan/SecurityCamera/raw/master/blog/new_aws_programmatic_user.png)
1. In the AWS console, [go to the IAM Users page](https://console.aws.amazon.com/iam/home#/users). Create a new user with **Access key - Programmatic access** enabled. We will allow Terraform to use this user for our project. Click **next** and then select `Attach existing policies directly` and click **next** without adding any policies (we will do that later). For tags, I recommend adding your project name with the key of `project` to help you with project-level billing in the future.
2. You will be given an Access Key ID and Secret Access Key -- keep this window open for now. We will save these credentials to AWS Vault so we no longer have to manage them manually: `aws-vault add <profile>` (replace `<profile>` with whatever you are calling your project). Add the credentials as prompted and when AWS Vault has saved your project's profile, you can press the close button on the AWS IAM Users page in your browser.
3. Test that everything is setup: `aws-vault exec <profile> -- aws sts get-caller-identity`. You should see your project's user ID and account returned.

## Configure Terraform 
1. Open the new file in your IDE (or download and use [Visual Studio Code](https://code.visualstudio.com/) if you don't have an IDE setup). 
2. 

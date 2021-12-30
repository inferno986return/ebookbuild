# `ebookbuild` - How to use Git

## Before Git

At the first company I worked for we simply mounted shared folders using the SMB protocol and altered the contents of the e-book project directly using File Explorer.

While this solution is acceptable for an individual or small team, I prefer using Git because it allows developers to log alterations made and is designed specifically for collaboration.

## Introduction to Git

Git is a version control system and a popular way of managing software development by ensuring code is backed up and easily retrievable. The Git project itself was designed by none other than Linus Torvalds himself who needed a way to manage the development of the Linux kernel.

Git can be hosted on a dedicated Git hosting site such as GitHub, GitLab or BitBucket. Or for full control can be self-hosted using software such as Bonobo, Gogs or even GitLab.
Use of Git is mandatory for anyone using GitHub and GitLab, as well as being supported by other source code hosting sites such as BitBucket. 

I recommend Git for e-book development because it is fast and e-book projects don’t tend to have large files (more than 50MB) or empty folders, which are some of Git's notable shortcomings.

This chapter will give a basic outline of how Git works and how to use it. However, Git is very popular and there’s plenty of documentation available for it, including an official book (which is available for free on the official Git website) – I won't make this guide completely definitive.

Using Git at first may seem intimidating as there are a lot of jargon words to learn. However, I will explain each core feature and by the end, you should be able to start setting up your first repository with some confidence.

## Git clients

To get started, I recommend using a Git client. There are a lot of Git clients, and official Git website keeps a list of them.

My personal choice of client is GitHub Desktop. GitHub Desktop is free and open-source with ports for Windows and macOS (and also albeit unofficially Debian, Fedora and AppImage). As its name heavily implies the client is owned by GitHub (now Microsoft) and connects with GitHub seamlessly, however it also supports connecting to other Git hosting services such as GitLab and Bitbucket along with self-hosted Git servers.

GitKraken is also a superb client with a beautiful user interface and has official builds for Windows, macOS and Ubuntu. However for commercial use users must pay $50 per year.

## Using Git 101

I find the easiest metaphor to describe Git is to think of a filing cabinet.

The repository is the cabinet itself and a branch is each drawer. You pull out a filing cabinet draw to access its contents, make your changes to the drawer, then note them down as a commit and you push the drawer closed when you are finished. A pull request in this analogy would be when one office worker requests access to another filing cabinet to alter a few files inside.

*Repository* - A repository is an instance of Git that covers an entire folder and its files. This is where a project will be placed and all the source code files and resources that make it.

*Commit* - A commit is an alteration made to the repository that has been accepted by the developer. This includes any changes made to the files and folders including editing the text files, adding files, deleting files, deleting files, etc. 
Most clients will show the differences between the files using colour-coding. A commit requires a short title for the Git log and optionally a longer description which can be handy for keeping track of development and writing notes.

*Push* - A push is the process of sending the commit from the development machine to the Git server.

*Pull* - A pull is the process of retrieving previously pushed data to the Git server back onto the development machine. Through a combination of pushing and pulling a developer can work on the same code on multiple machines.

*Pull Request* – A pull request is specific to Git hosting websites where a user requests permission for their commit to be pulled into the repository they don't have direct access to.

*Branch* - A branch is a particular version of a repository. By default, a Git repository uses the master (or main) branch and for basic Git use by an individual developer, this shouldn’t be a concern. For more complicated development, a branch can be merged bringing those changes to another branch or the branch can be split off. The way Git handles branching is the reason Git is referred to as a distributed source code management system.

## Clone a repository from GitHub using GitHub Desktop

As mentioned earlier, setting up GitHub Desktop with GitHub is a snap. First and foremost you need to decide if the repository is already on GitHub or you want to add a repository to GitHub.

If the repository is already on GitHub, you can make a local copy of that repository on your development machine’s hard drive:

1. Go to File → Clone repository… (Ctrl-Shift-O).
2. Select the “GitHub.com” tab (the default) and click the “Sign in” button.
3. Sign in to GitHub using your account.
4. Choose a repository to clone and the preferred folder for the repository on your development machine’s storage (by default, it’s placed in Documents/GitHub).

## Clone a repository from GitLab using GitHub Desktop

If the repository is already on GitLab it requires more involvement to make a copy on the development machine’s hard drive:

1. Login to GitLab.com in your preferred web browser, then select your preferred repository and copy the HTTPS link under the repository's name and description.
2. Create a SSH key to authenticate GitLab with GitHub desktop. This is done by opening up the Git Bash (Windows/macOS/GNU-Linux) or Terminal (macOS/GNU-Linux) then running this command (replace the e-mail in double-quotes with the GitLab account e-mail address): ssh-keygen -t rsa -C "your.email@example.com" -b 4096 then save the public-private key as a .pub file.
3. Authenticate the generated key by going to GitLab.com in your preferred browser and to your account’s settings and select “SSH Keys”. Add a new key by copying and pasting the public key half from the generated .pub file which begins with “ssh-rsa” into the text field then give it a name.
4. Go to File → Clone repository… (Ctrl-Shift-O).
5. Select the “URL” tab and paste the HTTPS link from earlier. Login to GitLab and then choose which repository to clone and where on the development machine’s hard drive to clone it to (the default is Documents/GitHub, but I rename it to Documents/GitLab).

## Committing and pushing to a repository in GitHub Desktop

Once changes have been made to the development machine’s copy of the repository, they can be committed to the repository on the Git server. GitHub Desktop makes committing a repository easy to do.

1. Select the files to commit and the branch to commit to (leave it as the Master branch if unsure).
2. Write a summary for the changes and if necessary a longer description.
3. Select “Submit” and then “Push origin”.
4. Select the “History” tab to ensure it has been committed properly.

## Further reading

* (Wikipedia page for Git)[https://en.wikipedia.org/wiki/Git], (archive)[https://archive.ph/Sm4Yf]
* (Git-SCM.com)[https://www.git-scm.com/] – the official website for the Git source code management tool with documentation on Git, a list of Git clients and a download for the current version.
* (Pro Git)[https://git-scm.com/book/en/v2] – the official and freely available book (and e-book) for Git which is available in multiple languages.
* (Learn Git)[https://try.github.io/] – GitHub’s official documentation on Git with many learning resources
* (Git Cheat Sheet)[https://about.gitlab.com/images/press/git-cheat-sheet.pdf] – a quick point of reference provided by GitLab showing a wide-range of common Git commands and what they do.
* (Git vs SVN)[https://backlog.com/blog/git-vs-svn-version-control-system/], (archive)[https://archive.ph/ysbaQ] – an insightful through rather advanced comparison of Git and SVN that suggests that one isn't necessarily superior to the other.

Cryptographic hash functions (CHFs) are the foundation of Protect.

The initial implementation of Protect uses SHA-256 as the CHF, but any CHF can be used.

Each filesystem object gets a hash record (HR). The general form of an HR is:

    HR(x) = Version || CHF(basename(x)) || CHF(contents(x))
    Version = 0x01

This version of the specification uses version 0x01. The payload length for
version 0x01 is 64 bytes. Thus, each HR record is 65 bytes in total. HR records
are simply concatened together.

Calculation of the HR depends on the type of filesystem object.

Normal files are the most straightforward:

    HR(normal_file) = Version || CHF(basename(file)) || CHF(contents(normal_file))

Protect never dereferences symbolic links. Instead, the target path of the
symbolic link is used as the contents:

    HR(symbolic_link) = Version || CHF(basename(symbolic_link)) || CHF(target(symbolic_link))

Directories are processed recursively. The HR of a directory is the CHF of the
concatened list of all of the filesystem objects directly below the directory.
Subdirectories are recursed in order to compute their own value. In other
words, it is a depth-first algorithm.

    HR(directory) = CHF(Sorted([HR List], key=basename))

For example, consider the following directory structure:

    /mnt/foo
       hello.txt = "hello, world\n"
       bar/
           hola.txt = "hola, mundo\n"

    The HRs are as follows:
    HR_hello = Version || CHF("hello.txt") || CHF("hello, world\n")
    HR_hola = Version || CHF("hola.txt") || CHF("hola, mundo\n")
    HR_bar = Version || CHF("bar") || CHF(HR_hola)
    HR_foo = Version || CHF("foo") || CHF(HR_bar || HR_hello)
    HR_mnt = Version || CHF("mnt") || CHF(HR_foo)

TODO:
    HR(special_file) = CHF(???)

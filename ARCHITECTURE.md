Cryptographic hash functions (CHFs) are the foundation of Protect.

Each filesystem object gets a hash record (HR). The general form of an HR is:

    HR(x) = Version || CHF(basename(x)) || CHF(contents(x))

The initial implementation sets Version = 0x01 and uses SHA-256 as the CHF.
Because SHA-256 hashes are 32 bytes long (in binary), that means the total
length of a version 1 HR is 32 + 32 = 64 bytes + version byte = 65 bytes total.

Thus, each version 0x01 HR record is 65 bytes in total.

An HRList is a sorted collection of HRs. First the HRs are put into a set. Then
the set is sorted. Finally, the set members are concatenated together.

    HRList(a, b, c, ...) = concatenate(sort([a, b, c, ...]))

Calculation of the HR depends on the type of filesystem object.

Normal files are the most straightforward:

    HR(normal_file) = Version || CHF(basename(file)) || CHF(contents(normal_file))

Protect never dereferences symbolic links. Instead, the target path of the
symbolic link is used as the contents:

    HR(symbolic_link) = Version || CHF(basename(symbolic_link)) || CHF(target(symbolic_link))

Directories are processed recursively. The HR of a directory is the CHF of the
HRList of all of the filesystem objects directly below the directory.
Subdirectories are recursed in order to compute their HRs.

    HR(directory) = CHF(HRList(directory objects))

For example, consider the following directory structure:

    /mnt/foo
       hello.txt = "hello, world\n"
       bar/
           hola.txt = "hola, mundo\n"

    The HRs are as follows:
    HR_hello = Version || CHF("hello.txt") || CHF("hello, world\n")
    HR_hola = Version || CHF("hola.txt") || CHF("hola, mundo\n")
    HR_bar = Version || CHF("bar") || CHF(HRList(HR_hola))
    HR_foo = Version || CHF("foo") || CHF(HRList(HR_bar, HR_hello))
    HR_mnt = Version || CHF("mnt") || CHF(HRList(HR_foo))

TODO:
    HR(special_file) = CHF(???)

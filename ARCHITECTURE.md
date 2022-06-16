Cryptographic hash functions (CHFs) are the foundation of Protect.

A Protect Hash Function is defined which incorporates a version, the
repository's public key, and the input to the CHF:

   PHF(x) = Version || CHF(PublicKey || x)

The initial implementation sets Version = 0x01 and uses SHA-256 as the CHF.

    PHF1(x) == 0x01 || SHA-256(PublicKey || x)

Each filesystem object gets a hash record (HR). The general form of an HR is:

    HR(file, contents) = PHF1(basename(file)) || PHF1(contents)

Because SHA-256 hashes are 32 bytes long (in binary), that means the total
length of a version 1 HR is (32 + 1) + (32 + 1) = 66 bytes total.

An HRList is a sorted collection of HRs. First the HRs are put into a set. Then
the set is sorted. Finally, the set members are concatenated together.

    HRList(a, b, c, ...) = concatenate(sort([a, b, c, ...]))

Calculation of the HR depends on the type of filesystem object.

Normal files are the most straightforward:

    HR_file(f) = HR(f, contents(f))

Protect never dereferences symbolic links. Instead, the target path of the
symbolic link is used as the contents:

    HR_symlink(sl) = HR(sl, target(sl))

Directories are processed recursively. The HR of a directory is the CHF of the
HRList of all of the filesystem objects directly below the directory.
Subdirectories are recursed in order to compute their HRs.

    HR_dir(d) = HR(d, HRList(list(d)))

For example, consider the following directory structure:

    /mnt/foo
       hello.txt = "hello, world\n"
       bar/
           hola.txt = "hola, mundo\n"
       zzz -> bar

    The HRs are as follows:

    HR_hello = HR_file(hello)
             = HR(hello, contents(hello))
             = PHF1(basename(file)) || PHF1("hello, world\n")
             = (0x01 || SHA-256(PublicKey || "hello.txt")) || (0x01 || SHA-256(PublicKey || "hello, world\n"))

    HR_hola  = HR_file(hola)
             = HR1(hola, "hola, mundo\n")
             = 0x01 || SHA-256("hola.txt") || SHA-256("hola, mundo\n")

    HR_zzz   = HR_symlink(zzz)
             = HR1(zzz, "bar")
             = 0x01 || SHA-256("zzz") || SHA-256("bar")

    HR_bar   = HR_dir(bar)
             = HR1(bar, HRList(list(bar)))
             = 0x01 || SHA-256("bar") || SHA-256(HRList(HR_hola))

    HR_foo   = HR_dir(foo)
             = HR1(foo, HRList(list(foo)))
             = 0x01 || SHA-256("foo") || SHA-256(HRList([HR_hello, HR_bar, HR_zzz]))


TODO:
    HR(special_file) = CHF(???)

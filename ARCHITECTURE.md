# Linux Filesystem Theory

Each filesystem entry has a stat object that contains a ctime (changed time).
Whenever a filesystem entry's contents change, Linux updates the ctime. For a
file, this means that any change to the file's contents will update the ctime.
For directories, only adding or removing a file from the directory will update
the directory's ctime. Changing the contents of an existing file will update
that file's ctime but not the directory's ctime.

In order to backup efficiently, Ark updates the ctime of any directory to the
newest ctime of any file in the directory with a newer ctime. This allows Ark
to use the ctime of the directory to know if the ctime of any object in the
directory has changed.




# Raw notes

remote filename - ark object

H() = CHF(PK || ...)

arkpath = f.H(timestamp).arkhash
  contents: blocks to reconstruct ?

All backup data stored by Ark is encrypted with the repository's public
key. And a design goal of Ark is to be able to back up without needing the
private key.

Every file has the following immutable characteristics that hold true
regardless of the storage method:
    - Filename
    - Contents
    - Hash of contents (derived)
    - Size

Some storage methods may provide additional characteristics, but they are
either not universally available or are not immutable (e.g., timestamp).

Consider a source file to be backed up, "hello" containing the contents "world\n":

    Filename: hello
    Contents: world\n

If any of these characteristics change, then the file can be considered as changed.

    Hash (Blake2): fe276ca3f323016ea43c87ec5e7c1cbb...
    Size: 6

    host, path, contents, timestamp -> SourceObj

    SourceObj(file) -> SourceFile
    SourceObj(directory) -> SourceDir

Starting with a file, we can store the (path, hash) of the file in order to see
if thas changed and the ctime to know whether it needs to be checked. This
information will be encoded in the filename. In order to avoid leaking
information, the public key will be used as a nonce.

FileContentsHash = HF1(file contents)
FilePathHash = HF1(file path)
FileCtimeHash = HF1(file ctime)

Concatenating these together yields a unique filename. Using "f." for file:

f.<path>.<contents>.<ctime>

At a later time, if the file hasn't changed, the expected remote path will be regenerated. Since it will exist, this means no further backup is needed.

If the ctime changes, then the contents hash and ctime will be recomputed.


Storage
  use cbor or messagepack

Crypto
  use GPG/PGP? AGE? DIY
  Mix in fs UUID and pubkey


The basic premise us to store metadata about the backup encrypted on the remote  file name has info so simply listing or exosfenxe check reveals info

input ctime basename contents
output filename and contents

filename contains hashed form of inputs
contents contain blocks needed to recinsreuct

parse path func
rerurns FsEbtry

inputs
filelist
ignored list
etc


Cryptographic hash functions (CHFs) are the foundation of Ark.

In Ark, the Hash Function (HF) is defined which incorporates a version, the
repository's public key, and the input:

   HF(PublicKey, x) = Version || CHF(PublicKey || x)

The initial implementation sets Version = 0x01 and uses SHA-256 as the CHF.

    HF1(x) == 0x01 || SHA-256(PublicKey || x)

Each filesystem object gets a hash record (HR). The general form of an HR is:

    HR(file, contents) = HF1(basename(file)) || HF1(contents)

Because SHA-256 hashes are 32 bytes long (in binary), that means the total
length of a version 1 HR is (32 + 1) + (32 + 1) = 66 bytes total.

An HRList is a sorted collection of HRs. First the HRs are put into a set. Then
the set is sorted. Finally, the set members are concatenated together.

    HRList(a, b, c, ...) = concatenate(sort([a, b, c, ...]))

Calculation of the HR depends on the type of filesystem object.

Normal files are the most straightforward:

    HR_file(f) = HR(f, contents(f))

Ark never dereferences symbolic links. Instead, the target path of the
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
             = HF1(basename(file)) || HF1("hello, world\n")
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

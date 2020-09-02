# snippet

```snippet``` allows you to create, view and use snippets on the command-line.

## Example

```
# To view a snippet:
$ snippet -t archive/extract_tar -v
tar -xvf <archive>

# To get the prefilled snippet:
$ snippet -t archive/extract_tar '/path/to/foo.tar'
tar -xvf /path/to/foo.tar

# To add a new snippet:
$ snippet -e archive/extract_tgz -f 'tar -xzvf <archive>'

# To interactively search snippets which include the term "extract":
$ snippet -t extract -v
```

## Setup

```
git clone https://github.com/bytebutcher/snippet
cd snippet
python3 -m venv venv
./venv/bin/python3 install -r requirements.txt
sudo ln -s $PWD/snippet /usr/bin/snippet
```

To enable bash-completion you might add following line to your .bashrc:
```bash
eval "$(register-python-argcomplete3 snippet)"
```
Make sure to add the ```snippet``` directory to your ```PATH``` or link it accordingly:
```
ln -s /path/to/snippet.py /usr/bin/snippet
```

## Usage

1. [Overview](#Overview)
2. [Assigning data to placeholders](#Assigning-data-to-placeholders)
   1. [Using positional arguments](#Using-positional-arguments)
   2. [Using environment variables](#Using-environment-variables)
   3. [Importing from csv-files](#Importing-from-csv-files)
   4. [Using presets](#Using-presets)
3. [Using string formats](#Using-string-formats)
   1. [Using the --format-string argument](#Using-the---format-string-argument)
   2. [Using input from a pipe](#Using-input-from-a-pipe)
   3. [Using templates](#Using-templates)
   4. [Using codecs](#Using-codecs)
   5. [Using optional arguments](#Using-optional-arguments)
   6. [Using defaults](#Using-defaults)
4. [Executing commands](#Executing-commands)
5. [See also](#See-also)

### Overview

The following overview shows various examples of how ```snippet``` can be used:
```
# Add or edit a snippet (will open vim)
$ snippet -e example
hello, <arg1>!

# Use the snippet with a custom argument
$ snippet -t example world
hello, world!

# Using on-the-fly transformation 
$ snippet -f "hello, <arg1>!" world
hello, world!

# Assigning multiple values and making use of presets
$ snippet -f "ping -c 1 <rhost> > ping_<rhost>_<date_time>.log;" rhost=localhost github.com
ping -c 1 localhost > ping_localhost_20770413000000.log;
ping -c 1 github.com > ping_github.com_20770413000000.log;

# Making use of repeatable placeholders
$ snippet -f "tar -czvf <archive> <file...>" archive.tgz file=file1 file2
tar -czvf archive.tgz file1 file2

# Using templates and reading arguments from a file
$ cat <<EOF > input.txt
localhost
github.com
EOF
$ snippet -t net/scan/nmap-ping rhost:hosts.txt
nmap -vvv -sP localhost -oA nmap-ping_localhost_20770413000000
nmap -vvv -sP github.com -oA nmap-ping_github.com_20770413000000

# Transforming strings
$ snippet -f "echo 'hello <arg1> (<arg1:b64>)';" snippet
echo 'hello snippet (cmV2YW1w)';
```

### Assigning data to placeholders
To assign data to a placeholder you have several options:

#### Using positional arguments
The most straight forward way of assigning data to a placeholder is to use positional arguments:

```
$ snippet -f "echo 'hello <arg1>';" snippet
echo 'hello snippet';
```

To assign multiple values to a specific placeholder you need to explicitly declare the placeholder to which the
value should be assigned to:
```
$ snippet -f "echo 'hello <arg1>';" arg1=snippet world
echo 'hello snippet';
echo 'hello world';
```

In addition values can be directly imported from a file:
```
$ cat <<EOF > input.txt
snippet
world
EOF
$ snippet -f "echo 'hello <arg1>';" arg1:input.txt
echo 'hello world';
echo 'hello snippet';
```

#### Using environment variables

```snippet``` evaluates environment variables and assigns data to any unset 
placeholder. To avoid running into conflict with other environment variables ```snippet``` only evaluates 
lower-case variable names:
```
$ export arg1=snippet
$ snippet -f "echo 'hello <arg1>';"
echo 'hello snippet';
```
To assign multiple values to a placeholder following syntax must be used:
```
$ export arg1="\('snippet' 'world'\)"
$ snippet -f "echo 'hello <arg1>';"
echo 'hello snippet';
echo 'hello world';
```

Note that positional arguments may override the evaluation of environment variables:
```
$ export arg1=snippet
$ snippet -f "echo 'hello <arg1>';" world
echo 'hello world';
```
 
#### Importing from csv-files

Data can also be imported from a csv-file using the ```-i | --import``` argument.
Note, that values must be separated by a tab character
 (which can be changed in ```.snippet/snippet_profile.py```):

```
$ cat <<EOF > input.csv
arg1    arg2
hello   snippet
        world
EOF
$ snippet -f "echo '<arg1> <arg2>';" -i input.csv 
echo 'hello world';
echo 'hello snippet';
```

#### Using presets

```snippet``` ships with a customizable set of preset placeholders which can be 
directly used in your format string 
(see ```.snippet/snippet_profile.py``` for more information). Preset placeholders may have constant  
but also dynamically generated values assigned to them:
```
$ snippet -f "echo '<date_time>';" 
echo '20200322034102';
```

### Using string formats

To use string formats you have several options:

#### Using the --format-string argument

If you read the previous section you already know the ```-f | --format-string``` argument:

```
$ snippet -f "echo 'hello snippet';"
echo 'hello snippet';
```

#### Using input from a pipe

Another option to set the string format is by using a pipe:
```
$ echo "echo 'hello snippet'" | snippet
echo 'hello snippet';
```

#### Using templates

If you want to persist your format string you can add them to ```snippet```'s template directory
which can be easily accessed using the interactive search prompt or the ```-t | --template``` argument:
```
$ mkdir -p ~/.snippet/templates
$ echo -n "echo '<arg1> <arg2> - <date_time>'" > ~/.snippet/templates/example

# Show an interactive search prompt
$ snippet arg1=hello arg2=snippet

# Select template by name
$ snippet -t example arg1=hello arg2=snippet
hello snippet - 20200322034102
```

If you have bash-completion enabled you can press ```<TAB>``` twice to autocomplete 
template names. 

To list all available templates you can use the ```-l | --list-templates```
parameter.

#### Using codecs

```snippet``` supports simple string transformation. A list of available codecs can be viewed by using the
```--list-codecs``` argument.

To transform a placeholder use the ```<PLACEHOLDER[:CODEC ...]>``` format:
```
$ snippet -f "<arg:b64>" "hello snippet"
aGVsbG8gcmV2YW1w
$ snippet -f "<arg> <arg:b64:b64>" "hello snippet"
hello snippet YUdWc2JHOGdjbVYyWVcxdw==
```

#### Using optional arguments

```snippet``` supports specifying optional parts in the string format by surrounding them with 
square-brackets:
```
$ snippet -f "<arg> [<arg2>]" hello snippet
hello snippet
$ snippet -f "<arg> [<arg2>]" hello
hello
```

If you need these characters to be part of the string format you need to
escape them accordingly:

```
$ snippet -f "\[<arg>\]" hello
[hello]
```

#### Using defaults

```snippet``` supports specifying default values for your placeholders:

```
$ snippet -f "<arg1> <arg2=default>" hello
hello default
```

### Executing commands

```snippet``` can be used to easily execute alternating commands in sequence:
```
$ snippet -f "echo 'hello <arg1>';" arg1=snippet world | bash
hello world
hello snippet
```

Using ```xargs``` the resulting commands can also be executed in parallel:
```
snippet -f "echo 'hello <arg1>';" arg1=snippet arg1=world | xargs --max-procs=4 -I CMD bash -c CMD
hello world
hello snippet
```

## See also

To make the most out of this tool you might also consider to look into the following projects:
* [leval](https://github.com/bytebutcher/leval) - the lesser eval
* [interactive](https://github.com/bytebutcher/interactive) - make arbitrary commands interactive
* [bgl](https://github.com/bytebutcher/bgl) - manage global bash environment variables

Here is a rather advanced example of how ```interactive```, ```leval``` and ```snippet``` play together:
```
# Make snippet interactive and evaluate output using leval before executing it
$ interactive -p "leval --print-stdout" snippet -f "[format]" [args]
```
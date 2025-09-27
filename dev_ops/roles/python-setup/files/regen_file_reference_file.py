import os
import sys, hashlib
import string

def regen_file_reference_file(
	inputDir: str,
	outputPath: str
):

	with open(outputPath,"w") as out:
		out.write("####### This file is generated. #######\n")
		out.write("# edit regen_file_reference_file #\n")
		out.write("# in mc_dev_ops.sh and rerun\n")
		out.write("from enum import Enum\n\n")
		out.write("class SqlScripts(Enum):\n")
		for dirPath, _, files in os.walk(inputDir):
			for file in sorted(files):
				filePath = f"{dirPath}/{file}"
				split = file.split(".")
				scriptName = split[1] if len(split) == 3 else split[0]
				trSet = string.punctuation + string.whitespace
				enumName = scriptName.translate(
					str.maketrans(trSet, "_" * len(trSet))
				).upper()
				with open(filePath, "r") as f:
					hashStr = hashlib.sha256(f.read().encode("utf-8")).hexdigest()
					relPath = filePath.removeprefix(inputDir + "/")
					out.write(
						f'\t{enumName} = (\n\t\t\"{relPath}\",\n\t\t\"{hashStr}\"\n\t)\n'
					)
		out.write("\n\t@property\n")
		out.write("\tdef file_name(self) -> str:\n")
		out.write("\t\treturn self.value[0]\n\n")
		out.write("\t@property\n")
		out.write("\tdef checksum(self) -> str:\n")
		out.write("\t\treturn self.value[1]\n")

if __name__ == "__main__":
	inputDir = sys.argv[1]
	outputPath = sys.argv[2]
	regen_file_reference_file(inputDir, outputPath)
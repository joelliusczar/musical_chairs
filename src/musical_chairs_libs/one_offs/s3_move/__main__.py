#pyright: reportMissingTypeStubs=false
from botocore.client import Config
import boto3
import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.tables as tbl
import os
import re



with dtos.DbConnectionProvider.get_configured_api_connection(
	"musical_chairs_db"
) as conn:
	with conn.begin() as transaction:
		query = tbl.songs.select()\
		.where(tbl.sg_internalpath.startswith("joellius"))\
		.limit(900).with_only_columns(tbl.sg_internalpath, tbl.sg_pk)
		records = conn.execute(query).fetchall()
		resource = boto3.resource( #pyright: ignore [reportUnknownMemberType]
		"s3",
		config=Config(
				signature_version='s3v4',
				region_name=dtos.ConfigAcessors.s3_region_name()
			)
		)
		bucket = resource.Bucket(dtos.ConfigAcessors.s3_bucket_name()) #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]

		prefix = ""

		quit()
		badKeys: list[str] = [
			o.key for o in bucket.objects.all() #pyright: ignore [reportUnknownArgumentType, reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
			if re.match(rf"{prefix}/.[^/].+", o.key) and "--" not in o.key #pyright: ignore [reportUnknownArgumentType, reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
		] #pyright: ignore [reportUnknownArgumentType, reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
		

		print(len(badKeys))

		badIds: list[int | None] = []
		for key in badKeys:
			print("")
			print(key)
			newKey = str(key).replace(f"{prefix}",f"{prefix}/--")
			# print(row[0])
			# print(newKey)
			newObj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
				bucket_name=dtos.ConfigAcessors.s3_bucket_name(),
				key=newKey
			)
			oldObj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
				bucket_name=dtos.ConfigAcessors.s3_bucket_name(),
				key=key
			)
			versionId = oldObj.version_id #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]

			print(versionId) #pyright: ignore [reportUnknownArgumentType]
			resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
				bucket_name=dtos.ConfigAcessors.s3_bucket_name(),
				key=newKey
			).copy_from(
				CopySource=os.path.join(dtos.ConfigAcessors.s3_bucket_name(),key)
			)
			print(f"copied? {newKey}")
			resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
				bucket_name=dtos.ConfigAcessors.s3_bucket_name(),
				key=key,
			).delete(VersionId=versionId)
			print(f"deleted {key}")


			


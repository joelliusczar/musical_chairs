#pyright: reportMissingTypeStubs=false
from botocore.client import Config
import boto3
import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.tables as tbl
import os
import sqlalchemy as sa


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
		
		prefix = ""
		badIds: list[int | None] = []
		for row in records:
			print("")
			print(row[0])
			newKey = str(row[0]).replace("joellius", prefix).replace("//","/--/")
			# print(row[0])
			# print(newKey)
			newObj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
				bucket_name=dtos.ConfigAcessors.s3_bucket_name(),
				key=newKey
			)
			oldObj = resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
				bucket_name=dtos.ConfigAcessors.s3_bucket_name(),
				key=row[0]
			)
			try:
				versionId = oldObj.version_id #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
			except:
				badIds.append(row[1])
				continue
			print(versionId) #pyright: ignore [reportUnknownArgumentType]
			resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
				bucket_name=dtos.ConfigAcessors.s3_bucket_name(),
				key=newKey
			).copy_from(
				CopySource=os.path.join(dtos.ConfigAcessors.s3_bucket_name(),row[0])
			)
			print(f"copied? {newKey}")
			resource.Object( #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]]
				bucket_name=dtos.ConfigAcessors.s3_bucket_name(),
				key=row[0],
			).delete(VersionId=versionId)
			print(f"deleted {row[0]}")
			conn.execute(
				sa.update(tbl.songs).values(internalpath = newKey)\
					.where(tbl.sg_internalpath == row[0])
			)
		# transaction.commit()
		print("badIds")
		print(badIds)
			


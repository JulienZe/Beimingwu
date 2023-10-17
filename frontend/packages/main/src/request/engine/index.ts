import { checkedFetch } from "../utils";
import { Learnware, Response } from "types";

const BASE_URL = "./api/engine";

function downloadLearnware({ id }: { id: string }): Promise<Response> {
  return checkedFetch(`${BASE_URL}/download_learnware?learnware_id=${id}`);
}

function getLearnwareDetailById({ id }: { id: string }): Promise<{
  code: number;
  msg: string;
  data: {
    learnware_info: Response.LearnwareDetailInfo;
  };
}> {
  return checkedFetch(`${BASE_URL}/learnware_info?learnware_id=${id}`).then((res) => res.json());
}

function getSemanticSpecification(): Promise<{
  data: {
    semantic_specification: Learnware.SemanticSpecification;
  };
}> {
  return checkedFetch(`${BASE_URL}/semantic_specification`).then((res) => res.json());
}

function searchLearnware({
  name,
  dataType,
  taskType,
  libraryType,
  tagList,
  files,
  page,
  limit,
}: {
  name: Learnware.Name;
  dataType: Learnware.DataType | "";
  taskType: Learnware.TaskType | "";
  libraryType: Learnware.LibraryType | "";
  tagList: Learnware.TagList;
  files: Learnware.Files;
  page: number;
  limit: number;
}): Promise<{
  code: number;
  msg: string;
  data: {
    learnware_list_single: Response.LearnwareSearchInfo[];
    learnware_list_multi: Response.LearnwareSearchInfo[];
    total_pages: number;
  };
}> {
  return getSemanticSpecification()
    .then((res) => {
      const semanticSpec = res.data.semantic_specification;
      semanticSpec.Name.Values = name || "";
      semanticSpec.Data.Values = (dataType && [dataType]) || [];
      semanticSpec.Task.Values = (taskType && [taskType]) || [];
      semanticSpec.Library.Values = (libraryType && [libraryType]) || [];
      semanticSpec.Scenario.Values = (tagList && tagList.map((tag) => tag)) || [];
      semanticSpec.Description.Values = "";

      const fd = new FormData();
      fd.append("semantic_specification", JSON.stringify(semanticSpec));
      fd.append("statistical_specification", (files.length > 0 && files[0]) || "");
      fd.append("limit", String(limit));
      fd.append("page", String(page));
      return fd;
    })
    .then((fd) =>
      checkedFetch(`${BASE_URL}/search_learnware`, {
        method: "POST",
        body: fd,
      }),
    )
    .then((res) => res.json());
}

export { downloadLearnware, getLearnwareDetailById, getSemanticSpecification, searchLearnware };
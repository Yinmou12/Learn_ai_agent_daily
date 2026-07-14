"""
定义响应结构

"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, field_validator


class ErrorDetail(BaseModel):
    """
    统一错误信息结构

    code 给程序看，message 给用户看。
    例如前端可以根据 code 判断应该弹出什么提示。
    """

    code: str = Field(description="错误代码")
    message: str = Field(description="错误说明")


class ApiResponse(BaseModel):
    """
    统一响应结构

    success 表示接口是否成功。
    data 放成功数据，error 放失败信息。

    这里 data 暂时用 Any，是为了降低初学阶段的泛型复杂度。
    后面熟悉 Pydantic 后，可以再改成泛型模型。
    """

    success: bool = Field(description="接口是否成功")
    data: Any | None = Field(default=None, description="成功时返回的数据")
    error: ErrorDetail | None = Field(default=None, description="失败是返回的错误")
    request_id: str | None = Field(default=None, description="请求ID")


class HealthResponse(BaseModel):
    """
    健康检查接口的响应模型。

    BaseModel 来自 Pydantic。
    你可以把它理解成：用 Python 类定义 JSON 的结构。
    """

    status: str = Field(description="服务状态")
    service: str = Field(description="服务名称")


class VersionData(BaseModel):
    """本接口返回的数据内容。"""

    version: str = Field(description="当前服务版本")


class ChatRequest(BaseModel):
    """
    聊天接口的请求模型。

    message 是用户输入给后端的问题。
    min_length 和 max_length 是第一层校验。
    field_validator 是第二层业务校验。
    """

    message: str = Field(
        min_length=1,
        max_length=500,
        description="用户输入的问题，长度为 1 到 500 个字符",
        examples=["用三句话解释 FastAPI 路由是什么"],
    )

    use_fake: bool = Field(
        default=False,
        description="是否使用假回答，True 表示不调用真实大模型",
    )

    # 先检查 message 的类型、长度等基础规则
    @field_validator("message")
    @classmethod
    def validation_message_not_blank(cls, value: str) -> str:
        """
        校验 message 不能只是空格。

        注意：
        min_length=1 只能拦住空字符串。
        但 "   " 的长度是3，所以必须手动 strip 后再判断。
        """

        message = value.strip()
        if not message:
            raise ValueError("message 不能为空")

        return message


class ChatResponse(BaseModel):
    """
    聊天接口的响应模型。

    今天先返回模拟回答。明天再把这里接到真实 LLMClient
    """

    message: str = Field(description="用户问题")
    answer: str = Field(description="后端生成的回答")
    model: str = Field(description="当前使用的模型名称")


class DebugPing(BaseModel):
    """
    debug ping 接口返回的数据内容
    """

    message: str = Field(description="调试接口返回消息")


class LoginRequest(BaseModel):
    """
    登录请求体。
    """

    username: str = Field(min_length=1, description="用户名")
    password: str = Field(min_length=1, description="密码")


class TokenData(BaseModel):
    """
    登陆成功后返回的数据。
    """

    access_token: str = Field(description="JWT token")
    token_type: str = Field(default="bearer", description="token 类型")


class UserProfile(BaseModel):
    """
    当前登录用户信息
    """

    id: int = Field(description="用户 ID")
    username: str = Field(description="用户名")
    display_name: str = Field(description="展示名称")


class UserCreate(BaseModel):
    """
    注册请求体
    """

    username: str = Field(
        min_length=3,
        max_length=50,
        description=f"用户名，长度 3 到 50",
    )

    password: str = Field(
        min_length=6,
        max_length=100,
        description=f"密码，长度至少 6",
    )

    display_name: str = Field(
        min_length=1,
        max_length=100,
        description=f"展示名称",
    )

    @field_validator("username")
    @classmethod
    def validation_username_not_blank(cls, value: str) -> str:
        """
        校验 username 不能只是空格。
        """

        username = value.strip()
        if not username:
            raise ValueError("username 不能为空")

        return username


class UserPublic(BaseModel):
    """对外返回的用户公开信息"""

    id: int = Field(description="用户 ID")
    username: str = Field(description="用户名")
    display_name: str = Field(description="展示名称")
    created_at: datetime = Field(description="创建时间")


class UserListData(BaseModel):
    """用户列表分页数据"""

    items: list[UserPublic] = Field(description="当前页用户列表")
    total: int = Field(description="总用户数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页用户数")


class ResumeParseRequest(BaseModel):
    """
    简历解析请求体
    """

    resume_text: str = Field(
        min_length=1, max_length=5000, description="用户的简历文本"
    )

    use_fake: bool = Field(
        default=True,
        description="是否使用假解析结果，True 表示不调用真实大模型",
    )

    @field_validator("resume_text")
    @classmethod
    def validate_resume_text_not_blank(cls, value: str) -> str:
        text = value.strip()

        if not text:
            raise ValueError("resume_text 不能为空")

        return text


class ResumeProfile(BaseModel):
    """
    结构化简历画像
    """

    name: str = Field(description="候选人姓名")
    skills: list[str] = Field(description="技能列表")
    years_of_experience: int = Field(default=0, description="工作或项目经验年限")
    target_roles: list[str] = Field(description="适合投递的岗位方向")
    summary: str = Field(description="候选人简要总结")

    @field_validator("skills")
    @classmethod
    def validate_skills_not_blank(cls, value: list[str]) -> list[str]:
        cleaned_skills = [skill.strip() for skill in value if skill.strip()]

        if not cleaned_skills:
            raise ValueError("skills 不能为空")

        return cleaned_skills


class ResumeRecordPublic(BaseModel):
    """
    对外返回的简历记录公开信息
    """

    id: int = Field(description="简历记录 ID")
    raw_text: str = Field(description="原始文本")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class JobMatchRequest(BaseModel):
    """
    岗位匹配请求体
    """

    jd_text: str = Field(
        min_length=1,
        max_length=500,
        description="岗位 JD 文本",
    )

    @field_validator("jd_text")
    @classmethod
    def validate_jd_text_not_blank(cls, value: str) -> str:
        jd_text = value.strip()

        if not jd_text:
            raise ValueError("jd_text 不能为空")

        return jd_text


class JobMatchResult(BaseModel):
    """
    岗位匹配结果
    """

    resume_id: int = Field(description="简历记录 ID")
    score: int = Field(description="匹配分数，范围 0 到 100")
    match_level: str = Field(descroption="匹配程度")
    matched_skills: list[str] = Field(description="JD 中命中的技能")
    missing_skills: list[str] = Field(description="JD 中没有体现或简历缺少的技能")
    suggestion: str = Field(description="投递建议")

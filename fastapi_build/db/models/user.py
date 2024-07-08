# -- coding: utf-8 --
# @Time : 2024/5/27 11:42
# @Author : PinBar
# @File : user.py
from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from core.context import g
from db.models.base import BaseModel, Base
from dao.user_dao import UserDao


class User(BaseModel):
    __tablename__ = 'user'
    objects = UserDao()
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), comment='username', nullable=True, index=True, unique=True)
    nickname = Column(String(32), comment='昵称', nullable=False)
    email = Column(String(32), comment='邮箱')
    password = Column(String(60), comment='密码')
    creator_id = Column(Integer, comment='创建人', nullable=True, default=lambda _: g.user_id)


class Parent(BaseModel):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(36))
    children = relationship("Child", back_populates="parent",
                            primaryjoin="Parent.id == foreign(Child.parent_id)", lazy='dynamic')

class Child(BaseModel):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(36))
    parent_id = Column(Integer, nullable=False)
    parent = relationship("Parent", back_populates="children",
                          primaryjoin="Parent.id == foreign(Child.parent_id)")


student_course_association = Table(
    'student_course', Base.metadata,
    Column('student_id', Integer, nullable=False),
    Column('course_id', Integer, nullable=False)
)

class Student(BaseModel):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    name = Column(String(36))
    courses = relationship(
        "Course",
        secondary=student_course_association,
        primaryjoin="Student.id == foreign(student_course.c.student_id)",
        secondaryjoin="Course.id == foreign(student_course.c.course_id)",
        back_populates="students",
        lazy='dynamic'  # Use dynamic loading
    )

class Course(BaseModel):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(String(36))
    students = relationship(
        "Student",
        secondary=student_course_association,
        primaryjoin="Course.id == foreign(student_course.c.course_id)",
        secondaryjoin="Student.id == foreign(student_course.c.student_id)",
        back_populates="courses",
        lazy='dynamic'  # Use dynamic loading
    )
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    fazendas = db.relationship('Fazenda', backref='dono', lazy=True)

class Fazenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    localizacao = db.Column(db.String(100))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    hortalicas = db.relationship('Hortalica', backref='fazenda', lazy=True)
    registros_hidricos = db.relationship('RegistroHidrico', backref='fazenda', lazy=True)

class Hortalica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_plantio = db.Column(db.String(20), nullable=False)
    data_colheita = db.Column(db.String(20))
    ciclo_estimado = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="Crescendo")
    fazenda_id = db.Column(db.Integer, db.ForeignKey('fazenda.id'), nullable=False)

class RegistroHidrico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nivel_porcentagem = db.Column(db.Float, nullable=False) # Valor percentual (%)
    data_leitura = db.Column(db.String(20), nullable=False)
    origem = db.Column(db.String(20), default="sensor") # Distingue 'simulador' de 'sensor'
    fazenda_id = db.Column(db.Integer, db.ForeignKey('fazenda.id'), nullable=False)

    # Alias / Propriedade de compatibilidade com versões anteriores
    @property
    def consumo_litros(self):
        return self.nivel_porcentagem

    @consumo_litros.setter
    def consumo_litros(self, valor):
        self.nivel_porcentagem = valor
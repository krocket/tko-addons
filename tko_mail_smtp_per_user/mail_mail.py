# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields


class ir_mail_server(osv.osv):
    _inherit = 'ir.mail_server'

    _columns = {
        'user_id': fields.many2one('res.users', string='Owner'),
    }

    _sql_constraints = [
        ('smtp_user_uniq', 'unique(user_id)', 'That user already has a SMTP server.'),
    ]

    def send_email(self, cr, uid, message, mail_server_id=None, smtp_server=None, smtp_port=None, smtp_user=None,
                   smtp_password=None, smtp_encryption=None, smtp_debug=False, context=None):
        message['Return-Path'] = message['From']
        return super(ir_mail_server, self).send_email(cr, uid, message, mail_server_id, smtp_server, smtp_port,
                                                      smtp_user, smtp_password, smtp_encryption, smtp_debug,
                                                      context=context)


class mail_mail(osv.Model):
    _inherit = 'mail.mail'

    def send(self, cr, uid, ids, auto_commit=False, raise_exception=False, context=None):
        for email in self.pool.get('mail.mail').browse(cr, uid, ids, context=context):
            user_id = email.mail_message_id.author_id.user_ids
            if user_id:
                server_id = self.pool.get('ir.mail_server').search(cr, uid, [('user_id', '=', user_id.id)],
                                                                   context=context)
                server_id = server_id and server_id[0] or False
                server_obj = self.pool.get('ir.mail_server').browse(cr, uid, [server_id],
                                                                    context=context)
                if server_id:
                    email_from = '%s <%s>' % (email.mail_message_id.author_id.name, server_obj.smtp_user)
                    self.write(cr, uid, ids, {'mail_server_id': server_id,
                                              'email_from': email_from,
                                              'reply_to': email_from},
                               context=context)
        return super(mail_mail, self).send(cr, uid, ids, auto_commit=auto_commit, raise_exception=raise_exception,
                                           context=context)
